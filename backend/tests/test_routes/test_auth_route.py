import pytest
import json
from flaskr.models.user_model import UserModel
from flaskr.utils import generate_password
from flaskr.db import db


class TestAuthRoute:
    """Test authentication routes."""

    def test_sign_in_success(self, client, app):
        """Test successful sign-in via POST endpoint."""
        with app.app_context():
            user = UserModel(
                username="testuser",
                email="test@example.com",
                password=generate_password("password123")
            )
            db.session.add(user)
            db.session.commit()

            response = client.post(
                "/api/v1/auth/sign-in",
                json={
                    "email": "test@example.com",
                    "password": "password123"
                },
                content_type="application/json"
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "token" in data
            assert data["token"] is not None

    def test_sign_in_invalid_credentials(self, client, app):
        """Test sign-in with invalid credentials."""
        with app.app_context():
            user = UserModel(
                username="testuser",
                email="test@example.com",
                password=generate_password("password123")
            )
            db.session.add(user)
            db.session.commit()

            response = client.post(
                "/api/v1/auth/sign-in",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword"
                },
                content_type="application/json"
            )

            assert response.status_code == 401

    def test_sign_in_missing_email(self, client):
        """Test sign-in with missing email field."""
        response = client.post(
            "/api/v1/auth/sign-in",
            json={
                "password": "password123"
            },
            content_type="application/json"
        )

        assert response.status_code == 422  # Validation error

    def test_sign_in_missing_password(self, client):
        """Test sign-in with missing password field."""
        response = client.post(
            "/api/v1/auth/sign-in",
            json={
                "email": "test@example.com"
            },
            content_type="application/json"
        )

        assert response.status_code == 422  # Validation error

    def test_sign_in_invalid_json(self, client):
        """Test sign-in with invalid JSON."""
        response = client.post(
            "/api/v1/auth/sign-in",
            data="invalid json",
            content_type="application/json"
        )

        assert response.status_code in [400, 422]
