import pytest
from unittest.mock import MagicMock
from AuthService import AuthService
from UserRepository import UserRepository

class TestIntegrationAuthService:
    def setup_method(self):
        self.mock_repo = MagicMock(spec=UserRepository)
        self.auth = AuthService(self.mock_repo)

    def test_successful_login_flow(self):
        self.mock_repo.get_user.return_value = {"password": "pass123"}
        self.mock_repo.update_last_login.return_value = True
        
        result = self.auth.login("valid_user", "pass123")
        
        assert result is True
        assert "valid_user" in self.auth.logged_in_users
        self.mock_repo.update_last_login.assert_called_once_with("valid_user")

    def test_incorrect_password_handling(self):
        self.mock_repo.get_user.return_value = {"password": "correct_pass"}
        
        result = self.auth.login("user", "wrong_pass")
        
        assert result is False
        assert "user" not in self.auth.logged_in_users
        self.mock_repo.update_last_login.assert_not_called()

    def test_nonexistent_user_login(self):
        self.mock_repo.get_user.return_value = None
        
        result = self.auth.login("ghost_user", "any_pass")
        
        assert result is False
        self.mock_repo.update_last_login.assert_not_called()

    def test_repository_error_propagation(self):
        self.mock_repo.get_user.return_value = {"password": "pass123"}
        self.mock_repo.update_last_login.side_effect = Exception("DB failure")
        
        with pytest.raises(Exception) as exc_info:
            self.auth.login("error_user", "pass123")
        assert "DB failure" in str(exc_info.value)
        assert "error_user" in self.auth.logged_in_users  # Added before failure

    def test_edge_case_empty_username(self):
        self.mock_repo.get_user.return_value = None
        
        result = self.auth.login("", "any_pass")
        assert result is False

    def test_real_integration_with_repository(self):
        real_repo = UserRepository()
        real_auth = AuthService(real_repo)
        
        assert real_auth.login("alice", "pass123") is True
        assert "alice" in real_auth.logged_in_users
        assert real_repo.users["alice"].get("last_login") == "2023-07-14"