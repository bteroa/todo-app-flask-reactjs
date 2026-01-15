import pytest
import json
from flaskr.models.task_model import TaskModel, TaskStatus
from flaskr.models.user_model import UserModel
from flaskr.models.tag_model import TagModel
from flaskr.utils import generate_password
from flaskr.db import db
from flask_jwt_extended import create_access_token


class TestTaskRoute:
    """Test task routes."""

    def test_get_tasks_on_user_success(self, client, app, sample_user, sample_tag):
        """Test GET /api/v1/tasks/user endpoint with JWT."""
        with app.app_context():
            task = TaskModel(
                title="Test Task",
                content="Content",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            db.session.add(task)
            db.session.commit()

            token = create_access_token(identity=str(sample_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.get(
                "/api/v1/tasks/user",
                headers=headers
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]["title"] == "Test Task"

    def test_get_tasks_on_user_no_jwt(self, client):
        """Test GET /api/v1/tasks/user without JWT token."""
        response = client.get("/api/v1/tasks/user")

        assert response.status_code == 401  # Unauthorized

    def test_create_task_success(self, client, app, sample_user, sample_tag):
        """Test POST /api/v1/tasks endpoint with JWT."""
        with app.app_context():
            token = create_access_token(identity=str(sample_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.post(
                "/api/v1/tasks",
                json={
                    "title": "New Task",
                    "content": "Task content",
                    "status": "PENDING",
                    "tagId": sample_tag.id
                },
                headers=headers,
                content_type="application/json"
            )

            assert response.status_code == 201

            # Verify task was created
            task = db.session.query(TaskModel).filter_by(title="New Task").first()
            assert task is not None
            assert task.user_id == sample_user.id

    def test_create_task_no_jwt(self, client):
        """Test POST /api/v1/tasks without JWT token."""
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "New Task",
                "content": "Task content",
                "status": "PENDING",
                "tagId": 1
            },
            content_type="application/json"
        )

        assert response.status_code == 401  # Unauthorized

    def test_create_task_missing_fields(self, client, app, sample_user):
        """Test POST /api/v1/tasks with missing required fields."""
        with app.app_context():
            token = create_access_token(identity=str(sample_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.post(
                "/api/v1/tasks",
                json={
                    "title": "New Task"
                },
                headers=headers,
                content_type="application/json"
            )

            assert response.status_code == 422  # Validation error

    def test_update_task_success(self, client, app, sample_task):
        """Test PUT /api/v1/tasks/<id> endpoint with JWT."""
        with app.app_context():
            token = create_access_token(identity=str(sample_task.user_id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.put(
                f"/api/v1/tasks/{sample_task.id}",
                json={
                    "title": "Updated Task",
                    "content": "Updated content",
                    "status": "COMPLETED"
                },
                headers=headers,
                content_type="application/json"
            )

            assert response.status_code == 200

            # Verify task was updated
            updated_task = db.session.query(TaskModel).filter_by(id=sample_task.id).first()
            assert updated_task.title == "Updated Task"
            assert updated_task.status == TaskStatus.COMPLETED

    def test_update_task_not_found(self, client, app, sample_user):
        """Test PUT /api/v1/tasks/<id> with non-existent task."""
        with app.app_context():
            token = create_access_token(identity=str(sample_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.put(
                "/api/v1/tasks/99999",
                json={
                    "title": "Updated Task",
                    "content": "Updated content",
                    "status": "COMPLETED"
                },
                headers=headers,
                content_type="application/json"
            )

            assert response.status_code == 404

    def test_update_task_no_jwt(self, client):
        """Test PUT /api/v1/tasks/<id> without JWT token."""
        response = client.put(
            "/api/v1/tasks/1",
            json={
                "title": "Updated Task",
                "content": "Updated content",
                "status": "COMPLETED"
            },
            content_type="application/json"
        )

        assert response.status_code == 401  # Unauthorized

    def test_delete_task_success(self, client, app, sample_task):
        """Test DELETE /api/v1/tasks/<id> endpoint with JWT."""
        with app.app_context():
            task_id = sample_task.id
            token = create_access_token(identity=str(sample_task.user_id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.delete(
                f"/api/v1/tasks/{task_id}",
                headers=headers
            )

            assert response.status_code == 204

            # Verify task was deleted
            task = db.session.query(TaskModel).filter_by(id=task_id).first()
            assert task is None

    def test_delete_task_not_found(self, client, app, sample_user):
        """Test DELETE /api/v1/tasks/<id> with non-existent task."""
        with app.app_context():
            token = create_access_token(identity=str(sample_user.id))
            headers = {"Authorization": f"Bearer {token}"}

            response = client.delete(
                "/api/v1/tasks/99999",
                headers=headers
            )

            assert response.status_code == 404

    def test_delete_task_no_jwt(self, client):
        """Test DELETE /api/v1/tasks/<id> without JWT token."""
        response = client.delete("/api/v1/tasks/1")

        assert response.status_code == 401  # Unauthorized
