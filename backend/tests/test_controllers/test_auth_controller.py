import pytest
from flask_smorest import abort
from flaskr.controllers.auth_controller import AuthController
from flaskr.models.user_model import UserModel
from flaskr.utils import generate_password
from flaskr.db import db
from unittest.mock import patch, MagicMock


class TestAuthController:
    """Test AuthController sign-in functionality."""

    def test_sign_in_success(self, app):
        """Test successful sign-in with valid credentials."""
        with app.app_context():
            user = UserModel(
                username="testuser",
                email="test@example.com",
                password=generate_password("password123")
            )
            db.session.add(user)
            db.session.commit()

            data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            result = AuthController.sign_in(data)
            
            assert "token" in result
            assert result["token"] is not None
            assert isinstance(result["token"], str)

    def test_sign_in_invalid_email(self, app):
        """Test sign-in with non-existent user email."""
        with app.app_context():
            data = {
                "email": "nonexistent@example.com",
                "password": "password123"
            }
            
            with pytest.raises(abort) as exc_info:
                AuthController.sign_in(data)
            
            assert exc_info.value.status_code == 401
            assert "Incorrect credentials" in str(exc_info.value)

    def test_sign_in_invalid_password(self, app):
        """Test sign-in with wrong password."""
        with app.app_context():
            user = UserModel(
                username="testuser",
                email="test@example.com",
                password=generate_password("correctpassword")
            )
            db.session.add(user)
            db.session.commit()

            data = {
                "email": "test@example.com",
                "password": "wrongpassword"
            }
            
            with pytest.raises(abort) as exc_info:
                AuthController.sign_in(data)
            
            assert exc_info.value.status_code == 401
            assert "Incorrect credentials" in str(exc_info.value)

    def test_sign_in_database_error(self, app):
        """Test sign-in with database error."""
        with app.app_context():
            data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            with patch('flaskr.controllers.auth_controller.db.session.execute') as mock_execute:
                mock_execute.side_effect = Exception("Database error")
                
                with pytest.raises(abort) as exc_info:
                    AuthController.sign_in(data)
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)
