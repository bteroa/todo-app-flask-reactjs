import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from config import TestConfig
from flaskr import create_app
from flaskr.db import db
from flaskr.models.user_model import UserModel
from flaskr.models.tag_model import TagModel
from flaskr.models.task_model import TaskModel, TaskStatus
from flaskr.utils import generate_password


@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Create JWT token headers for authenticated requests."""
    with app.app_context():
        user = UserModel(
            username="testuser",
            email="test@example.com",
            password=generate_password("testpass123")
        )
        db.session.add(user)
        db.session.commit()
        
        token = create_access_token(identity=str(user.id))
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user(app):
    """Create a sample user in the database."""
    with app.app_context():
        user = UserModel(
            username="sampleuser",
            email="sample@example.com",
            password=generate_password("password123")
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def sample_tag(app):
    """Create a sample tag in the database."""
    with app.app_context():
        tag = TagModel(name="Work")
        db.session.add(tag)
        db.session.commit()
        db.session.refresh(tag)
        return tag


@pytest.fixture
def sample_task(app, sample_user, sample_tag):
    """Create a sample task in the database."""
    with app.app_context():
        task = TaskModel(
            title="Test Task",
            content="This is a test task",
            status=TaskStatus.PENDING,
            user_id=sample_user.id,
            tag_id=sample_tag.id
        )
        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)
        return task


@pytest.fixture
def multiple_users(app):
    """Create multiple users for testing."""
    with app.app_context():
        users = []
        for i in range(3):
            user = UserModel(
                username=f"user{i+1}",
                email=f"user{i+1}@example.com",
                password=generate_password("password123")
            )
            db.session.add(user)
            users.append(user)
        db.session.commit()
        for user in users:
            db.session.refresh(user)
        return users


@pytest.fixture
def multiple_tags(app):
    """Create multiple tags for testing."""
    with app.app_context():
        tags = []
        tag_names = ["Work", "Personal", "Shopping"]
        for name in tag_names:
            tag = TagModel(name=name)
            db.session.add(tag)
            tags.append(tag)
        db.session.commit()
        for tag in tags:
            db.session.refresh(tag)
        return tags
