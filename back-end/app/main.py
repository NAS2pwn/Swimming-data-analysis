from fastapi import FastAPI
from app.api.endpoints import auth, data
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.db.session import engine

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    await init_db(db)
    db.close()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(data.router, prefix="/data", tags=["data"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Swimming Olympics API"}
