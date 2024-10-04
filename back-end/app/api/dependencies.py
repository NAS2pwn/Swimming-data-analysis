from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import SessionLocal

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()  # Crée une nouvelle session
    try:
        yield db  # Utilise la session
    finally:
        db.close()  # Ferme la session après utilisation
