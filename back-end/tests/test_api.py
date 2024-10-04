from fastapi.testclient import TestClient
from app.main import app
import unittest
from unittest.mock import patch, MagicMock
from app.schemas.user import UserCreate
from app.crud.user import create_user

client = TestClient(app)

class TestEndpoints(unittest.TestCase):
    def test_read_main(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the Swimming Olympics API"}

    @patch('app.crud.user.Session')
    def test_create_user(self, mock_session):
        user_data = UserCreate(email="test@test.fr", password="hehehe")
        
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        created_user = create_user(mock_db, user_data)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        assert created_user.email == user_data.email
        assert created_user.is_admin == False
        assert hasattr(created_user, 'api_key')
        assert created_user.hashed_password != user_data.password
