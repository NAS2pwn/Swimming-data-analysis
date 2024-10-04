from sqlalchemy.orm import Session
from app.crud.user import get_user_by_email, create_user
from app.schemas.user import UserCreate
from app.core.config import settings
from app.models.models import Base, User
from app.db.session import engine
from app.db.data_importer import DataImporter
import os

async def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=engine)
    
    user = get_user_by_email(db, email=settings.FIRST_ADMIN_EMAIL)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_ADMIN_EMAIL,
            password=settings.FIRST_ADMIN_PASSWORD,
        )
        user = create_user(db, user=user_in, is_admin=True)
        print(f"Created first admin: {user.email}")
    else:
        print("First admin already exists")
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', settings.CSV_FILENAME)
    data_importer = DataImporter(db, csv_path)
    data_importer.import_data()
    