import pytest
from flaskr import create_app
from config import DevelopmentConfig, TestConfig
from flaskr.db import db
from flaskr.extensions import migrate, api, cors, jwt


class TestAppInitialization:
    """Test Flask app initialization."""

    def test_create_app_default_config(self):
        """Test app creation with default config."""
        app = create_app()
        
        assert app is not None
        assert app.config["SQLALCHEMY_DATABASE_URI"] == DevelopmentConfig.SQLALCHEMY_DATABASE_URI
        assert app.config["JWT_SECRET_KEY"] == DevelopmentConfig.JWT_SECRET_KEY

    def test_create_app_test_config(self):
        """Test app creation with test config."""
        app = create_app(TestConfig)
        
        assert app is not None
        assert app.config["SQLALCHEMY_DATABASE_URI"] == TestConfig.SQLALCHEMY_DATABASE_URI
        assert app.config["TESTING"] is True

    def test_blueprint_registration(self, app):
        """Test that blueprints are registered."""
        # Check that blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        assert "auth" in blueprint_names
        assert "users" in blueprint_names
        assert "tags" in blueprint_names
        assert "tasks" in blueprint_names

    def test_extension_initialization(self, app):
        """Test that extensions are initialized."""
        assert db is not None
        assert migrate is not None
        assert api is not None
        assert cors is not None
        assert jwt is not None

    def test_database_initialization(self, app):
        """Test that database can be initialized."""
        with app.app_context():
            db.create_all()
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            assert "users" in tables
            assert "tasks" in tables
            assert "tags" in tables

    def test_app_config_values(self, app):
        """Test that app has correct config values."""
        assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
        assert app.config["API_TITLE"] == "Rest API"
        assert app.config["API_VERSION"] == "v1"
        assert app.config["OPENAPI_VERSION"] == "3.0.2"

    def test_app_testing_mode(self, app):
        """Test that app is in testing mode when using TestConfig."""
        assert app.config["TESTING"] is True
