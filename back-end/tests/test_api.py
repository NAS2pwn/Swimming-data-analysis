from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from app.models.models import User
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Swimming Olympics API"}

#def test_endpoint_create_user():
