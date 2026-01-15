import pytest
from flask_smorest import abort
from flaskr.controllers.task_controller import TaskController
from flaskr.models.task_model import TaskModel, TaskStatus
from flaskr.models.user_model import UserModel
from flaskr.models.tag_model import TagModel
from flaskr.utils import generate_password
from flaskr.db import db
from unittest.mock import patch


class TestTaskController:
    """Test TaskController CRUD operations."""

    def test_get_all_tasks_on_user(self, app, sample_user, sample_tag):
        """Test getting all tasks for a user."""
        with app.app_context():
            task1 = TaskModel(
                title="Task 1",
                content="Content 1",
                status=TaskStatus.PENDING,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            task2 = TaskModel(
                title="Task 2",
                content="Content 2",
                status=TaskStatus.IN_PROGRESS,
                user_id=sample_user.id,
                tag_id=sample_tag.id
            )
            db.session.add_all([task1, task2])
            db.session.commit()

            with patch('flaskr.controllers.task_controller.get_jwt_identity', return_value=str(sample_user.id)):
                result = TaskController.get_all_on_user()
            
            assert len(result) == 2
            assert all(hasattr(task, 'id') for task in result)
            assert all(hasattr(task, 'title') for task in result)
            assert all(hasattr(task, 'tag_name') for task in result)

    def test_get_all_tasks_on_user_empty(self, app, sample_user):
        """Test getting all tasks when user has no tasks."""
        with app.app_context():
            with patch('flaskr.controllers.task_controller.get_jwt_identity', return_value=str(sample_user.id)):
                result = TaskController.get_all_on_user()
            
            assert len(result) == 0
            assert isinstance(result, list)

    def test_create_task_success(self, app, sample_user, sample_tag):
        """Test creating a task successfully."""
        with app.app_context():
            data = {
                "title": "New Task",
                "content": "Task content",
                "status": "PENDING",
                "tagId": sample_tag.id
            }
            
            with patch('flaskr.controllers.task_controller.get_jwt_identity', return_value=str(sample_user.id)):
                TaskController.create(data)
            
            task = db.session.query(TaskModel).filter_by(title="New Task").first()
            assert task is not None
            assert task.title == "New Task"
            assert task.content == "Task content"
            assert task.status == TaskStatus.PENDING
            assert task.user_id == sample_user.id
            assert task.tag_id == sample_tag.id

    def test_create_task_database_error(self, app, sample_user, sample_tag):
        """Test creating task with database error."""
        with app.app_context():
            data = {
                "title": "New Task",
                "content": "Task content",
                "status": "PENDING",
                "tagId": sample_tag.id
            }
            
            with patch('flaskr.controllers.task_controller.get_jwt_identity', return_value=str(sample_user.id)):
                with patch('flaskr.controllers.task_controller.db.session.commit') as mock_commit:
                    mock_commit.side_effect = Exception("Database error")
                    
                    with pytest.raises(abort) as exc_info:
                        TaskController.create(data)
                    
                    assert exc_info.value.status_code == 500
                    assert "Internal server error" in str(exc_info.value)

    def test_update_task_success(self, app, sample_task):
        """Test updating a task successfully."""
        with app.app_context():
            data = {
                "title": "Updated Task",
                "content": "Updated content",
                "status": "COMPLETED"
            }
            
            TaskController.update(data, sample_task.id)
            
            updated_task = db.session.query(TaskModel).filter_by(id=sample_task.id).first()
            assert updated_task.title == "Updated Task"
            assert updated_task.content == "Updated content"
            assert updated_task.status == TaskStatus.COMPLETED

    def test_update_task_not_found(self, app):
        """Test updating a task that doesn't exist."""
        with app.app_context():
            data = {
                "title": "Updated Task",
                "content": "Updated content",
                "status": "COMPLETED"
            }
            
            with pytest.raises(abort) as exc_info:
                TaskController.update(data, 99999)
            
            assert exc_info.value.status_code == 404
            assert "Task not found" in str(exc_info.value)

    def test_update_task_database_error(self, app, sample_task):
        """Test updating task with database error."""
        with app.app_context():
            data = {
                "title": "Updated Task",
                "content": "Updated content",
                "status": "COMPLETED"
            }
            
            with patch('flaskr.controllers.task_controller.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Database error")
                
                with pytest.raises(abort) as exc_info:
                    TaskController.update(data, sample_task.id)
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)

    def test_delete_task_success(self, app, sample_task):
        """Test deleting a task successfully."""
        with app.app_context():
            task_id = sample_task.id
            
            TaskController.delete(task_id)
            
            task = db.session.query(TaskModel).filter_by(id=task_id).first()
            assert task is None

    def test_delete_task_not_found(self, app):
        """Test deleting a task that doesn't exist."""
        with app.app_context():
            with pytest.raises(abort) as exc_info:
                TaskController.delete(99999)
            
            assert exc_info.value.status_code == 404
            assert "Task not found" in str(exc_info.value)

    def test_delete_task_database_error(self, app, sample_task):
        """Test deleting task with database error."""
        with app.app_context():
            with patch('flaskr.controllers.task_controller.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Database error")
                
                with pytest.raises(abort) as exc_info:
                    TaskController.delete(sample_task.id)
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)

    def test_get_all_tasks_on_user_database_error(self, app, sample_user):
        """Test getting all tasks with database error."""
        with app.app_context():
            with patch('flaskr.controllers.task_controller.get_jwt_identity', return_value=str(sample_user.id)):
                with patch('flaskr.controllers.task_controller.db.session.query') as mock_query:
                    mock_query.side_effect = Exception("Database error")
                    
                    with pytest.raises(abort) as exc_info:
                        TaskController.get_all_on_user()
                    
                    assert exc_info.value.status_code == 500
                    assert "Internal server error" in str(exc_info.value)
