import pytest
import json
from flaskr.models.tag_model import TagModel
from flaskr.db import db


class TestTagRoute:
    """Test tag routes."""

    def test_get_all_tags(self, client, app, multiple_tags):
        """Test GET /api/v1/tags endpoint."""
        with app.app_context():
            response = client.get("/api/v1/tags")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 3
            assert all("name" in tag for tag in data)

    def test_get_all_tags_empty(self, client, app):
        """Test GET /api/v1/tags when database is empty."""
        with app.app_context():
            response = client.get("/api/v1/tags")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 0

    def test_create_tag_success(self, client, app):
        """Test POST /api/v1/tags endpoint."""
        with app.app_context():
            response = client.post(
                "/api/v1/tags",
                json={
                    "name": "NewTag"
                },
                content_type="application/json"
            )

            assert response.status_code == 201

            # Verify tag was created
            tag = db.session.query(TagModel).filter_by(name="NewTag").first()
            assert tag is not None

    def test_create_tag_duplicate(self, client, app, sample_tag):
        """Test POST /api/v1/tags with duplicate name."""
        with app.app_context():
            response = client.post(
                "/api/v1/tags",
                json={
                    "name": sample_tag.name
                },
                content_type="application/json"
            )

            assert response.status_code == 409

    def test_create_tag_missing_name(self, client):
        """Test POST /api/v1/tags with missing name field."""
        response = client.post(
            "/api/v1/tags",
            json={},
            content_type="application/json"
        )

        assert response.status_code == 422  # Validation error

    def test_create_tag_invalid_json(self, client):
        """Test POST /api/v1/tags with invalid JSON."""
        response = client.post(
            "/api/v1/tags",
            data="invalid json",
            content_type="application/json"
        )

        assert response.status_code in [400, 422]
