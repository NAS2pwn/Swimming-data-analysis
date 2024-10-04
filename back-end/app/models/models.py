from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    api_key = Column(String, unique=True, index=True)
    is_admin = Column(Boolean, default=False)

class Athlete(Base):
    __tablename__ = 'athletes'
    
    athlete_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    gender = Column(String)

class Event(Base):
    __tablename__ = 'events'
    
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String)
    year = Column(Integer)
    distance = Column(Integer)
    stroke = Column(String)
    is_relay = Column(Boolean)
    nb_relay = Column(Integer, nullable=True)

class NationalTeam(Base):
    __tablename__ = 'national_teams'
    
    national_team_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String)

class EventTeam(Base):
    __tablename__ = 'event_teams'
    
    event_team_id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('events.event_id'))
    athlete_id = Column(Integer, ForeignKey('athletes.athlete_id'))
    national_team_id = Column(Integer, ForeignKey('national_teams.national_team_id'))

class Result(Base):
    __tablename__ = 'results'
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    event_team_id = Column(Integer, ForeignKey('event_teams.event_team_id'))
    results = Column(Float, nullable=True)
    rank = Column(Integer)
    quit_reason = Column(String, nullable=True)