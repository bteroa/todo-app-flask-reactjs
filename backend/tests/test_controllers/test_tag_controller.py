import pytest
from flask_smorest import abort
from flaskr.controllers.tag_controller import TagController
from flaskr.models.tag_model import TagModel
from flaskr.db import db
from unittest.mock import patch


class TestTagController:
    """Test TagController CRUD operations."""

    def test_get_all_tags(self, app, multiple_tags):
        """Test getting all tags."""
        with app.app_context():
            result = TagController.get_all()
            
            assert len(result) == 3
            assert all(isinstance(tag, TagModel) for tag in result)
            assert {tag.name for tag in result} == {"Work", "Personal", "Shopping"}

    def test_get_all_tags_empty(self, app):
        """Test getting all tags when database is empty."""
        with app.app_context():
            result = TagController.get_all()
            
            assert len(result) == 0
            assert isinstance(result, list)

    def test_get_all_tags_limit(self, app):
        """Test that get_all limits to 15 tags."""
        with app.app_context():
            # Create more than 15 tags
            for i in range(20):
                tag = TagModel(name=f"Tag{i}")
                db.session.add(tag)
            db.session.commit()
            
            result = TagController.get_all()
            
            assert len(result) <= 15

    def test_create_tag_success(self, app):
        """Test creating a tag successfully."""
        with app.app_context():
            data = {
                "name": "NewTag"
            }
            
            TagController.create(data)
            
            tag = db.session.query(TagModel).filter_by(name="NewTag").first()
            assert tag is not None
            assert tag.name == "NewTag"

    def test_create_tag_duplicate(self, app, sample_tag):
        """Test creating tag with duplicate name."""
        with app.app_context():
            data = {
                "name": sample_tag.name
            }
            
            with pytest.raises(abort) as exc_info:
                TagController.create(data)
            
            assert exc_info.value.status_code == 409
            assert "Tag already registered" in str(exc_info.value)

    def test_create_tag_database_error(self, app):
        """Test creating tag with database error."""
        with app.app_context():
            data = {
                "name": "NewTag"
            }
            
            with patch('flaskr.controllers.tag_controller.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Database error")
                
                with pytest.raises(abort) as exc_info:
                    TagController.create(data)
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)

    def test_get_all_tags_database_error(self, app):
        """Test getting all tags with database error."""
        with app.app_context():
            with patch('flaskr.controllers.tag_controller.db.session.execute') as mock_execute:
                mock_execute.side_effect = Exception("Database error")
                
                with pytest.raises(abort) as exc_info:
                    TagController.get_all()
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)
