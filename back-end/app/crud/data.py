from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.models.models import Event

def get_swimming_categories(db: Session):
    swimming_data = (
        db.query(Event.is_relay, Event.distance, Event.nb_relay, Event.stroke)
        .order_by(Event.stroke, Event.nb_relay)
        .all()
    )
    
    # Calculer total_distance
    categories = [
        {
            "is_relay": event.is_relay,
            "total_distance": event.nb_relay * event.distance if event.nb_relay else event.distance,
            "stroke": event.stroke
        }
        for event in swimming_data
    ]
    
    return categories
