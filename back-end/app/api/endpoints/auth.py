from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.crud.user import create_user, authenticate_user, regenerate_api_key
from app.schemas.user import UserCreate, User, UserLogin
from app.core.security import admin_required, get_current_user

router = APIRouter()

@router.post("/create_user/", response_model=User)
def create_new_user(user: UserCreate, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    return create_user(db=db, user=user)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user.email, user.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {"access_token": user.api_key, "token_type": "bearer"}

@router.post("/test")
def test():
    return {"message": "Hello World"}

@router.post("/regenerate-api-key", response_model=User)
def regenerate_user_api_key(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return regenerate_api_key(db, current_user.id)
