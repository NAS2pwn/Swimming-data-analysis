import pandas as pd
from sqlalchemy.orm import Session
from app.models.models import Athlete, Event, NationalTeam, EventTeam, Result
import re
import numpy as np

class DataImporter:
    def __init__(self, session: Session, csv_path: str):
        self.session = session
        self.csv_path = csv_path
        self.df = None

    def import_data(self):
        self._load_and_preprocess_data()
        self._import_to_database()
    
    def _load_and_preprocess_data(self):
        print(self.csv_path)
        self.df = pd.read_csv(self.csv_path)
        print(self.df.head())
        self._rename_columns()
        self._process_is_relay()
        self._process_distance()
        self._process_results()
        self._process_athletes()
    
    def _rename_columns(self):
        self.df=self.df.rename(columns={
            'Location': 'location',
            'Year': 'year',
            'Distance (in meters)': 'distance',
            'Stroke': 'stroke',
            'Relay?': 'is_relay',
            'Gender': 'gender',
            'Team': 'team',
            'Athlete': 'athlete',
            'Results': 'results',
            'Rank': 'rank'
        })
        
    def _process_is_relay(self):
        self.df['is_relay'] = self.df['is_relay'].apply(lambda x: True if x == 'Yes' else False)
    
    def _process_distance(self):
        def extract_distance_and_relay(distance_str):
            if 'x' in distance_str:
                nb_relay_str, distance_str = re.findall(r'\d+', distance_str)
                print(nb_relay_str, distance_str)
                return int(distance_str), int(nb_relay_str)
            else:
                distance = int(re.findall(r'\d+', distance_str)[0])
                return distance, 1
            
        self.df['distance'], self.df['nb_relay'] = zip(*self.df['distance'].apply(extract_distance_and_relay))
    
    def _process_results(self):
        def clean_time_str(time_str):
            if isinstance(time_str, str):
                # Extraire les chiffres et les séparateurs pertinents
                cleaned = re.match(r'^(\d+:?\d*:?\d*\.?\d*)', time_str)
                if cleaned:
                    return cleaned.group(1)
                elif not re.search(r'\d', time_str):
                    return time_str  # Retourner la chaîne si elle ne contient aucun chiffre
            return time_str

        def convert_to_seconds(time_str):
            original_value = time_str
            time_str = clean_time_str(time_str)
            
            if isinstance(time_str, float):
                return time_str, None  # Déjà en secondes
            elif isinstance(time_str, str):
                if ':' in time_str:
                    # Format 00:04:37.510000
                    time_parts = time_str.split(':')
                    if len(time_parts) == 3:
                        hours, minutes, seconds = time_parts
                        total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    else:
                        minutes, seconds = time_parts
                        total_seconds = int(minutes) * 60 + float(seconds)
                elif re.match(r'^\d+(\.\d+)?$', time_str):
                    # Format 59.720
                    total_seconds = float(time_str)
                else:
                    return np.nan, original_value  # Cas de disqualification ou format invalide
            else:
                return np.nan, str(original_value)  # Cas où le type n'est pas reconnu
            
            return round(total_seconds, 3), None  # Arrondir à 3 décimales pour la précision milliseconde

        self.df['results'], self.df['quit_reason'] = zip(*self.df['results'].apply(convert_to_seconds))

    def _process_athletes(self):
        self.df['athlete'] = self.df['athlete'].fillna("Unknown")

        relay_rows = []

        # Itérer sur chaque ligne du DataFrame
        for index, row in self.df.iterrows():
            if row['is_relay']:
                athletes = row['athlete'].split(',')  # Séparer les noms des athlètes
                for athlete in athletes:
                    relay_rows.append({
                        'id': len(relay_rows) + 1,  # ID autoincrémenté
                        'location': row['location'],
                        'year': row['year'],
                        'distance': row['distance'],
                        'stroke': row['stroke'],
                        'is_relay': row['is_relay'],
                        'gender': row['gender'],
                        'team': row['team'],
                        'athlete': athlete.strip(),  # Enlever les espaces
                        'results': row['results'],
                        'rank': row['rank'],
                        'nb_relay': row['nb_relay']
                    })
            else:
                relay_rows.append({
                    'id': len(relay_rows) + 1,
                    'location': row['location'],
                    'year': row['year'],
                    'distance': row['distance'],
                    'stroke': row['stroke'],
                    'is_relay': row['is_relay'],
                    'gender': row['gender'],
                    'team': row['team'],
                    'athlete': row['athlete'],
                    'results': row['results'],
                    'rank': row['rank'],
                    'nb_relay': row['nb_relay']
                })

        # Créer un nouveau DataFrame à partir des lignes de relais
        self.df = pd.DataFrame(relay_rows)    
    
    def _import_to_database(self):
        for _, row in self.df.iterrows():
            athlete = self._get_or_create_athlete(row['athlete'], row['gender'])
            national_team = self._get_or_create_national_team(row['team'])
            event = self._get_or_create_event(row['location'], row['year'], row['distance'], row['stroke'], row['is_relay'], row['nb_relay'])
            event_team = self._get_or_create_team(event.event_id, athlete.athlete_id, national_team.national_team_id)
            self._get_or_create_result(event_team.event_team_id, row['results'], row['rank'], row.get('quit_reason'))

        self.session.commit()

    def _get_or_create_athlete(self, name, gender):
        athlete = self.session.query(Athlete).filter_by(name=name, gender=gender).first()
        if not athlete:
            athlete = Athlete(name=name, gender=gender)
            self.session.add(athlete)
            self.session.flush()
        return athlete

    def _get_or_create_national_team(self, code):
        team = self.session.query(NationalTeam).filter_by(code=code).first()
        if not team:
            team = NationalTeam(code=code)
            self.session.add(team)
            self.session.flush()
        return team

    def _get_or_create_event(self, location, year, distance, stroke, is_relay, nb_relay):
        nb_relay = None if is_relay == False else int(nb_relay)
        event = self.session.query(Event).filter_by(
            location=location, year=year, distance=distance, 
            stroke=stroke, is_relay=is_relay, nb_relay=nb_relay
        ).first()
        if not event:
            event = Event(location=location, year=year, distance=distance, 
                          stroke=stroke, is_relay=is_relay, nb_relay=nb_relay)
            self.session.add(event)
            self.session.flush()
        return event

    def _get_or_create_team(self, event_id, athlete_id, national_team_id):
        team = self.session.query(EventTeam).filter_by(
            event_id=event_id, athlete_id=athlete_id, national_team_id=national_team_id
        ).first()
        if not team:
            team = EventTeam(event_id=event_id, athlete_id=athlete_id, national_team_id=national_team_id)
            self.session.add(team)
            self.session.flush()
        return team

    def _get_or_create_result(self, event_team_id, results, rank, quit_reason):
        result = self.session.query(Result).filter_by(
            event_team_id=event_team_id, results=results, rank=rank
        ).first()
        if not result:
            result = Result(event_team_id=event_team_id, results=results, rank=rank, quit_reason=quit_reason)
            self.session.add(result)
            self.session.flush()
        return result