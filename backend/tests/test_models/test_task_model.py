import pytest
from datetime import datetime, timezone
from flaskr.models.task_model import TaskModel, TaskStatus
from flaskr.models.user_model import UserModel
from flaskr.models.tag_model import TagModel
from flaskr.db import db
from flaskr.utils import generate_password


class TestTaskModel:
    """Test TaskModel creation, status enum, and relationships."""

    def test_create_task(self, app, sample_user, sample_tag):
        """Test creating a task with valid data."""
        with app.app_context():
            task = TaskModel(
                title="New Task",
                content="Task content",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            assert task.title == "New Task"
            assert task.content == "Task content"
            assert task.status == TaskStatus.PENDING
            assert task.user_id == sample_user.id
            assert task.tag_id == sample_tag.id

    def test_task_save_to_database(self, app, sample_user, sample_tag):
        """Test saving a task to the database."""
        with app.app_context():
            task = TaskModel(
                title="Save Task",
                content="Content",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            db.session.add(task)
            db.session.commit()
            
            assert task.id is not None
            assert task.id > 0
            assert task.created_at is not None
            assert isinstance(task.created_at, datetime)

    def test_task_status_enum(self, app, sample_user, sample_tag):
        """Test task status enum values."""
        with app.app_context():
            task_pending = TaskModel(
                title="Pending Task",
                content="Content",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            assert task_pending.status == TaskStatus.PENDING
            assert task_pending.status.value == "PENDING"

            task_in_progress = TaskModel(
                title="In Progress Task",
                content="Content",
                status=TaskStatus.IN_PROGRESS,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            assert task_in_progress.status == TaskStatus.IN_PROGRESS
            assert task_in_progress.status.value == "IN_PROGRESS"

            task_completed = TaskModel(
                title="Completed Task",
                content="Content",
                status=TaskStatus.COMPLETED,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            assert task_completed.status == TaskStatus.COMPLETED
            assert task_completed.status.value == "COMPLETED"

    def test_task_default_status(self, app, sample_user, sample_tag):
        """Test that task defaults to PENDING status."""
        with app.app_context():
            task = TaskModel(
                title="Default Task",
                content="Content",
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            # Status should default to PENDING
            assert task.status == TaskStatus.PENDING

    def test_task_relationship_with_user(self, app, sample_user, sample_tag):
        """Test task relationship with user."""
        with app.app_context():
            task = TaskModel(
                title="User Task",
                content="Content",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            db.session.add(task)
            db.session.commit()

            assert task.user is not None
            assert task.user.id == sample_user.id
            assert task.user.username == sample_user.username

    def test_task_relationship_with_tag(self, app, sample_user, sample_tag):
        """Test task relationship with tag."""
        with app.app_context():
            task = TaskModel(
                title="Tag Task",
                content="Content",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            db.session.add(task)
            db.session.commit()

            assert task.tag is not None
            assert task.tag.id == sample_tag.id
            assert task.tag.name == sample_tag.name

    def test_task_created_at_timestamp(self, app, sample_user, sample_tag):
        """Test that task has created_at timestamp."""
        with app.app_context():
            before_creation = datetime.now(timezone.utc)
            task = TaskModel(
                title="Timestamp Task",
                content="Content",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            db.session.add(task)
            db.session.commit()
            after_creation = datetime.now(timezone.utc)

            assert task.created_at is not None
            assert before_creation <= task.created_at <= after_creation

    def test_task_update_status(self, app, sample_task):
        """Test updating task status."""
        with app.app_context():
            assert sample_task.status == TaskStatus.PENDING
            
            sample_task.status = TaskStatus.IN_PROGRESS
            db.session.commit()
            
            updated_task = db.session.query(TaskModel).filter_by(id=sample_task.id).first()
            assert updated_task.status == TaskStatus.IN_PROGRESS

            updated_task.status = TaskStatus.COMPLETED
            db.session.commit()
            
            final_task = db.session.query(TaskModel).filter_by(id=sample_task.id).first()
            assert final_task.status == TaskStatus.COMPLETED

    def test_task_update_content(self, app, sample_task):
        """Test updating task content."""
        with app.app_context():
            sample_task.title = "Updated Title"
            sample_task.content = "Updated Content"
            db.session.commit()
            
            updated_task = db.session.query(TaskModel).filter_by(id=sample_task.id).first()
            assert updated_task.title == "Updated Title"
            assert updated_task.content == "Updated Content"

    def test_task_foreign_key_constraint_user(self, app, sample_tag):
        """Test that task requires valid user_id."""
        with app.app_context():
            task = TaskModel(
                title="Invalid Task",
                content="Content",
                status=TaskStatus.PENDING,
                user_id=99999,  # Non-existent user
                tag_id=sample_tag.id
            )
            db.session.add(task)
            
            with pytest.raises(Exception):  # Should raise IntegrityError or similar
                db.session.commit()

    def test_task_foreign_key_constraint_tag(self, app, sample_user):
        """Test that task requires valid tag_id."""
        with app.app_context():
            task = TaskModel(
                title="Invalid Task",
                content="Content",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=99999  # Non-existent tag
            )
            db.session.add(task)
            
            with pytest.raises(Exception):  # Should raise IntegrityError or similar
                db.session.commit()
