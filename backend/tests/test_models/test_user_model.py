import pytest
from flaskr.models.user_model import UserModel
from flaskr.models.task_model import TaskModel
from flaskr.db import db
from flaskr.utils import generate_password, check_password
from sqlalchemy.exc import IntegrityError


class TestUserModel:
    """Test UserModel creation, relationships, and constraints."""

    def test_create_user(self, app):
        """Test creating a user with valid data."""
        with app.app_context():
            user = UserModel(
                username="testuser",
                email="test@example.com",
                password=generate_password("password123")
            )
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.password is not None
            assert user.id is None  # Not yet committed

    def test_user_save_to_database(self, app):
        """Test saving a user to the database."""
        with app.app_context():
            user = UserModel(
                username="testuser",
                email="test@example.com",
                password=generate_password("password123")
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.id > 0

    def test_user_unique_username(self, app):
        """Test that username must be unique."""
        with app.app_context():
            user1 = UserModel(
                username="testuser",
                email="test1@example.com",
                password=generate_password("password123")
            )
            db.session.add(user1)
            db.session.commit()

            user2 = UserModel(
                username="testuser",
                email="test2@example.com",
                password=generate_password("password123")
            )
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_user_unique_email(self, app):
        """Test that email must be unique."""
        with app.app_context():
            user1 = UserModel(
                username="user1",
                email="test@example.com",
                password=generate_password("password123")
            )
            db.session.add(user1)
            db.session.commit()

            user2 = UserModel(
                username="user2",
                email="test@example.com",
                password=generate_password("password123")
            )
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_user_relationship_with_tasks(self, app, sample_user, sample_tag):
        """Test user relationship with tasks."""
        with app.app_context():
            task = TaskModel(
                title="Test Task",
                content="Content",
                status="PENDING",
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            db.session.add(task)
            db.session.commit()

            assert len(sample_user.tasks) == 1
            assert sample_user.tasks[0].title == "Test Task"
            assert sample_user.tasks[0].user_id == sample_user.id

    def test_user_cascade_delete_tasks(self, app, sample_user, sample_tag):
        """Test that deleting a user cascades to delete their tasks."""
        with app.app_context():
            task1 = TaskModel(
                title="Task 1",
                content="Content 1",
                status="PENDING",
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            task2 = TaskModel(
                title="Task 2",
                content="Content 2",
                status="PENDING",
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            db.session.add_all([task1, task2])
            db.session.commit()

            user_id = sample_user.id
            db.session.delete(sample_user)
            db.session.commit()

            # Verify tasks are deleted
            tasks = db.session.query(TaskModel).filter_by(user_id=user_id).all()
            assert len(tasks) == 0

    def test_user_query_by_username(self, app):
        """Test querying user by username."""
        with app.app_context():
            user = UserModel(
                username="queryuser",
                email="query@example.com",
                password=generate_password("password123")
            )
            db.session.add(user)
            db.session.commit()

            found_user = db.session.query(UserModel).filter_by(username="queryuser").first()
            assert found_user is not None
            assert found_user.username == "queryuser"
            assert found_user.email == "query@example.com"

    def test_user_query_by_email(self, app):
        """Test querying user by email."""
        with app.app_context():
            user = UserModel(
                username="emailuser",
                email="email@example.com",
                password=generate_password("password123")
            )
            db.session.add(user)
            db.session.commit()

            found_user = db.session.query(UserModel).filter_by(email="email@example.com").first()
            assert found_user is not None
            assert found_user.username == "emailuser"
