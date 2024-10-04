from fastapi import APIRouter, Depends
from typing import List
from app.schemas.data import SwimmingCategory
from app.crud.data import get_swimming_categories
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

@router.get("/swimming_categories", response_model=List[SwimmingCategory])
async def swimming_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = get_swimming_categories(db)
    return categories
