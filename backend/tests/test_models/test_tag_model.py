import pytest
from flaskr.models.tag_model import TagModel
from flaskr.models.task_model import TaskModel
from flaskr.db import db
from sqlalchemy.exc import IntegrityError


class TestTagModel:
    """Test TagModel creation, uniqueness, and relationships."""

    def test_create_tag(self, app):
        """Test creating a tag with valid data."""
        with app.app_context():
            tag = TagModel(name="Work")
            assert tag.name == "Work"
            assert tag.id is None  # Not yet committed

    def test_tag_save_to_database(self, app):
        """Test saving a tag to the database."""
        with app.app_context():
            tag = TagModel(name="Personal")
            db.session.add(tag)
            db.session.commit()
            
            assert tag.id is not None
            assert tag.id > 0

    def test_tag_unique_name(self, app):
        """Test that tag name must be unique."""
        with app.app_context():
            tag1 = TagModel(name="UniqueTag")
            db.session.add(tag1)
            db.session.commit()

            tag2 = TagModel(name="UniqueTag")
            db.session.add(tag2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_tag_relationship_with_tasks(self, app, sample_tag, sample_user):
        """Test tag relationship with tasks."""
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

            assert len(sample_tag.tasks) == 2
            assert sample_tag.tasks[0].tag_id == sample_tag.id
            assert sample_tag.tasks[1].tag_id == sample_tag.id

    def test_tag_cascade_delete_tasks(self, app, sample_tag, sample_user):
        """Test that deleting a tag cascades to delete its tasks."""
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

            tag_id = sample_tag.id
            db.session.delete(sample_tag)
            db.session.commit()

            # Verify tasks are deleted
            tasks = db.session.query(TaskModel).filter_by(tag_id=tag_id).all()
            assert len(tasks) == 0

    def test_tag_query_by_name(self, app):
        """Test querying tag by name."""
        with app.app_context():
            tag = TagModel(name="QueryTag")
            db.session.add(tag)
            db.session.commit()

            found_tag = db.session.query(TagModel).filter_by(name="QueryTag").first()
            assert found_tag is not None
            assert found_tag.name == "QueryTag"

    def test_tag_multiple_tags(self, app):
        """Test creating multiple tags."""
        with app.app_context():
            tags = [
                TagModel(name="Tag1"),
                TagModel(name="Tag2"),
                TagModel(name="Tag3")
            ]
            db.session.add_all(tags)
            db.session.commit()

            all_tags = db.session.query(TagModel).all()
            assert len(all_tags) == 3
            assert {tag.name for tag in all_tags} == {"Tag1", "Tag2", "Tag3"}
