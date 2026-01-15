import pytest
from flask_smorest import abort
from flaskr.controllers.user_controller import UserController
from flaskr.models.user_model import UserModel
from flaskr.utils import generate_password
from flaskr.db import db
from unittest.mock import patch


class TestUserController:
    """Test UserController CRUD operations."""

    def test_get_all_users(self, app, multiple_users):
        """Test getting all users."""
        with app.app_context():
            result = UserController.get_all()
            
            assert len(result) == 3
            assert all(isinstance(user, UserModel) for user in result)
            assert {user.username for user in result} == {"user1", "user2", "user3"}

    def test_get_all_users_empty(self, app):
        """Test getting all users when database is empty."""
        with app.app_context():
            result = UserController.get_all()
            
            assert len(result) == 0
            assert isinstance(result, list)

    def test_get_user_by_id_success(self, app, sample_user):
        """Test getting user by ID successfully."""
        with app.app_context():
            result = UserController.get_by_id(sample_user.id)
            
            assert result is not None
            assert isinstance(result, UserModel)
            assert result.id == sample_user.id
            assert result.username == sample_user.username
            assert result.email == sample_user.email

    def test_get_user_by_id_not_found(self, app):
        """Test getting user by ID when user doesn't exist."""
        with app.app_context():
            with pytest.raises(abort) as exc_info:
                UserController.get_by_id(99999)
            
            assert exc_info.value.status_code == 404
            assert "User not found" in str(exc_info.value)

    def test_create_user_success(self, app):
        """Test creating a user successfully."""
        with app.app_context():
            data = {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
            
            UserController.create(data)
            
            user = db.session.query(UserModel).filter_by(username="newuser").first()
            assert user is not None
            assert user.username == "newuser"
            assert user.email == "newuser@example.com"
            assert user.password is not None
            assert user.password != "password123"  # Should be hashed

    def test_create_user_duplicate_username(self, app, sample_user):
        """Test creating user with duplicate username."""
        with app.app_context():
            data = {
                "username": sample_user.username,
                "email": "different@example.com",
                "password": "password123"
            }
            
            with pytest.raises(abort) as exc_info:
                UserController.create(data)
            
            assert exc_info.value.status_code == 409
            assert "Username already registered" in str(exc_info.value)

    def test_create_user_duplicate_email(self, app, sample_user):
        """Test creating user with duplicate email."""
        with app.app_context():
            data = {
                "username": "differentuser",
                "email": sample_user.email,
                "password": "password123"
            }
            
            with pytest.raises(abort) as exc_info:
                UserController.create(data)
            
            assert exc_info.value.status_code == 409
            assert "Email already registered" in str(exc_info.value)

    def test_create_user_database_error(self, app):
        """Test creating user with database error."""
        with app.app_context():
            data = {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
            
            with patch('flaskr.controllers.user_controller.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Database error")
                
                with pytest.raises(abort) as exc_info:
                    UserController.create(data)
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)

    def test_delete_user_success(self, app, sample_user):
        """Test deleting user successfully."""
        with app.app_context():
            user_id = sample_user.id
            
            # Mock JWT identity
            with patch('flaskr.controllers.user_controller.get_jwt_identity', return_value=str(user_id)):
                UserController.delete()
            
            user = db.session.query(UserModel).filter_by(id=user_id).first()
            assert user is None

    def test_delete_user_not_found(self, app):
        """Test deleting user that doesn't exist."""
        with app.app_context():
            with patch('flaskr.controllers.user_controller.get_jwt_identity', return_value="99999"):
                with pytest.raises(abort) as exc_info:
                    UserController.delete()
                
                assert exc_info.value.status_code == 404
                assert "User not found" in str(exc_info.value)

    def test_delete_user_database_error(self, app, sample_user):
        """Test deleting user with database error."""
        with app.app_context():
            with patch('flaskr.controllers.user_controller.get_jwt_identity', return_value=str(sample_user.id)):
                with patch('flaskr.controllers.user_controller.db.session.commit') as mock_commit:
                    mock_commit.side_effect = Exception("Database error")
                    
                    with pytest.raises(abort) as exc_info:
                        UserController.delete()
                    
                    assert exc_info.value.status_code == 500
                    assert "Internal server error" in str(exc_info.value)

    def test_get_all_users_database_error(self, app):
        """Test getting all users with database error."""
        with app.app_context():
            with patch('flaskr.controllers.user_controller.db.session.execute') as mock_execute:
                mock_execute.side_effect = Exception("Database error")
                
                with pytest.raises(abort) as exc_info:
                    UserController.get_all()
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)

    def test_get_user_by_id_database_error(self, app):
        """Test getting user by ID with database error."""
        with app.app_context():
            with patch('flaskr.controllers.user_controller.db.session.execute') as mock_execute:
                mock_execute.side_effect = Exception("Database error")
                
                with pytest.raises(abort) as exc_info:
                    UserController.get_by_id(1)
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)
