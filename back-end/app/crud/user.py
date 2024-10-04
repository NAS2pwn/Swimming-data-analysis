from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
import uuid

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate, is_admin: bool = False):
    hashed_password = get_password_hash(user.password)
    api_key = str(uuid.uuid4())
    db_user = User(email=user.email, hashed_password=hashed_password, api_key=api_key, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def regenerate_api_key(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.api_key = str(uuid.uuid4())
        db.commit()
        db.refresh(user)
    return user
