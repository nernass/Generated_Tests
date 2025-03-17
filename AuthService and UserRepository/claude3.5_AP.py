import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from AuthService import AuthService
from UserRepository import UserRepository

class TestAuthServiceIntegration:
    @pytest.fixture
    def mock_repository(self):
        repo = Mock(spec=UserRepository)
        repo.users = {
            "alice": {"password": "pass123", "role": "admin"},
            "bob": {"password": "pass456", "role": "user"}
        }
        repo.get_user.side_effect = lambda username: repo.users.get(username)
        repo.update_last_login.side_effect = lambda username: username in repo.users
        return repo

    @pytest.fixture
    def auth_service(self, mock_repository):
        return AuthService(mock_repository)

    # Success Path Tests
    def test_successful_login_flow(self, auth_service, mock_repository):
        result = auth_service.login("alice", "pass123")
        assert result == True
        assert "alice" in auth_service.logged_in_users
        mock_repository.get_user.assert_called_once_with("alice")
        mock_repository.update_last_login.assert_called_once_with("alice")

    def test_successful_multiple_logins(self, auth_service):
        assert auth_service.login("alice", "pass123") == True
        assert auth_service.login("bob", "pass456") == True
        assert set(auth_service.logged_in_users) == {"alice", "bob"}

    # Failure Path Tests
    def test_failed_login_wrong_password(self, auth_service, mock_repository):
        result = auth_service.login("alice", "wrongpass")
        assert result == False
        assert "alice" not in auth_service.logged_in_users
        mock_repository.update_last_login.assert_not_called()

    def test_repository_failure(self, auth_service, mock_repository):
        mock_repository.get_user.side_effect = Exception("Database connection failed")
        with pytest.raises(Exception, match="Database connection failed"):
            auth_service.login("alice", "pass123")
        assert "alice" not in auth_service.logged_in_users

    def test_update_last_login_failure(self, auth_service, mock_repository):
        mock_repository.update_last_login.return_value = False
        result = auth_service.login("alice", "pass123")
        assert result == True  # Current implementation doesn't check update_last_login result
        assert "alice" in auth_service.logged_in_users

    # Edge Cases
    def test_empty_credentials(self, auth_service):
        assert auth_service.login("", "") == False
        assert auth_service.login("alice", "") == False
        assert auth_service.login("", "pass123") == False

    def test_none_values(self, auth_service):
        assert auth_service.login(None, "pass123") == False
        assert auth_service.login("alice", None) == False
        assert auth_service.login(None, None) == False

    def test_long_credentials(self, auth_service):
        long_string = "x" * 10000
        assert auth_service.login(long_string, "pass123") == False
        assert auth_service.login("alice", long_string) == False

    # Data Flow Tests
    def test_user_data_flow(self, auth_service, mock_repository):
        auth_service.login("alice", "pass123")
        mock_repository.get_user.assert_called_once_with("alice")
        user_data = mock_repository.get_user("alice")
        assert user_data["role"] == "admin"
        assert user_data["password"] == "pass123"

    def test_login_state_persistence(self, auth_service, mock_repository):
        auth_service.login("alice", "pass123")
        auth_service.login("alice", "wrongpass")  # Should not affect logged_in state
        assert "alice" in auth_service.logged_in_users
        assert mock_repository.update_last_login.call_count == 1

    # Cascade Tests
    def test_error_cascade(self, auth_service, mock_repository):
        mock_repository.get_user.return_value = None
        result = auth_service.login("unknown", "pass123")
        assert result == False
        mock_repository.update_last_login.assert_not_called()
        assert "unknown" not in auth_service.logged_in_users