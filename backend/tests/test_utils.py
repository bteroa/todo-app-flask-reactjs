import pytest
from flaskr.utils import generate_password, check_password


class TestUtils:
    """Test utility functions."""

    def test_generate_password(self):
        """Test password hashing."""
        password = "testpassword123"
        password_hash = generate_password(password)
        
        assert password_hash is not None
        assert isinstance(password_hash, str)
        assert password_hash != password  # Should be hashed
        assert len(password_hash) > 0

    def test_generate_password_different_hashes(self):
        """Test that same password generates different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = generate_password(password)
        hash2 = generate_password(password)
        
        # Hashes should be different due to random salt
        assert hash1 != hash2

    def test_check_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        password_hash = generate_password(password)
        
        result = check_password(password_hash, password)
        
        assert result is True

    def test_check_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        password_hash = generate_password(password)
        
        result = check_password(password_hash, wrong_password)
        
        assert result is False

    def test_check_password_different_hashes_same_password(self):
        """Test that different hashes of same password both verify correctly."""
        password = "testpassword123"
        hash1 = generate_password(password)
        hash2 = generate_password(password)
        
        # Both hashes should verify the same password
        assert check_password(hash1, password) is True
        assert check_password(hash2, password) is True

    def test_check_password_empty_password(self):
        """Test password verification with empty password."""
        password_hash = generate_password("somepassword")
        
        result = check_password(password_hash, "")
        
        assert result is False

    def test_generate_password_empty_string(self):
        """Test generating password hash for empty string."""
        password_hash = generate_password("")
        
        assert password_hash is not None
        assert isinstance(password_hash, str)
