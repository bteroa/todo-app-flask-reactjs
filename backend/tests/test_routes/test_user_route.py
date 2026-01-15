import pytest
import json
from flaskr.models.user_model import UserModel
from flaskr.utils import generate_password
from flaskr.db import db
from flask_jwt_extended import create_access_token


class TestUserRoute:
    """Test user routes."""

    def test_get_all_users(self, client, app, multiple_users):
        """Test GET /api/v1/users endpoint."""
        with app.app_context():
            response = client.get("/api/v1/users")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 3

    def test_get_user_by_id(self, client, app, sample_user):
        """Test GET /api/v1/users/<id> endpoint."""
        with app.app_context():
            response = client.get(f"/api/v1/users/{sample_user.id}")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["id"] == sample_user.id
            assert data["username"] == sample_user.username

    def test_get_user_by_id_not_found(self, client, app):
        """Test GET /api/v1/users/<id> with non-existent user."""
        with app.app_context():
            response = client.get("/api/v1/users/99999")

            assert response.status_code == 404

    def test_create_user_success(self, client, app):
        """Test POST /api/v1/users endpoint."""
        with app.app_context():
            response = client.post(
                "/api/v1/users",
                json={
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "password123"
                },
                content_type="application/json"
            )

            assert response.status_code == 201

            # Verify user was created
            user = db.session.query(UserModel).filter_by(username="newuser").first()
            assert user is not None

    def test_create_user_duplicate_username(self, client, app, sample_user):
        """Test POST /api/v1/users with duplicate username."""
        with app.app_context():
            response = client.post(
                "/api/v1/users",
                json={
                    "username": sample_user.username,
                    "email": "different@example.com",
                    "password": "password123"
                },
                content_type="application/json"
            )

            assert response.status_code == 409

    def test_create_user_duplicate_email(self, client, app, sample_user):
        """Test POST /api/v1/users with duplicate email."""
        with app.app_context():
            response = client.post(
                "/api/v1/users",
                json={
                    "username": "differentuser",
                    "email": sample_user.email,
                    "password": "password123"
                },
                content_type="application/json"
            )

            assert response.status_code == 409

    def test_create_user_missing_fields(self, client):
        """Test POST /api/v1/users with missing required fields."""
        response = client.post(
            "/api/v1/users",
            json={
                "username": "newuser"
            },
            content_type="application/json"
        )

        assert response.status_code == 422  # Validation error

    def test_delete_user_account_success(self, client, app, sample_user):
        """Test DELETE /api/v1/users/account endpoint with JWT."""
        with app.app_context():
            token = create_access_token(identity=str(sample_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.delete(
                "/api/v1/users/account",
                headers=headers
            )

            assert response.status_code == 204

            # Verify user was deleted
            user = db.session.query(UserModel).filter_by(id=sample_user.id).first()
            assert user is None

    def test_delete_user_account_no_jwt(self, client):
        """Test DELETE /api/v1/users/account without JWT token."""
        response = client.delete("/api/v1/users/account")

        assert response.status_code == 401  # Unauthorized

    def test_delete_user_account_invalid_jwt(self, client):
        """Test DELETE /api/v1/users/account with invalid JWT token."""
        headers = {"Authorization": "Bearer invalid_token"}

        response = client.delete(
            "/api/v1/users/account",
            headers=headers
        )

        assert response.status_code == 422  # Invalid token
