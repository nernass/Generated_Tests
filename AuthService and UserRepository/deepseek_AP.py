import pytest
from unittest.mock import MagicMock
from AuthService import AuthService
from UserRepository import UserRepository

class TestIntegrationAuthService:
    def setup_method(self):
        self.mock_repo = MagicMock(spec=UserRepository)
        self.auth = AuthService(self.mock_repo)

    def test_valid_login_flow(self):
        self.mock_repo.get_user.return_value = {"password": "valid_pass"}
        self.mock_repo.update_last_login.return_value = True
        
        result = self.auth.login("test_user", "valid_pass")
        
        assert result is True
        self.mock_repo.get_user.assert_called_once_with("test_user")
        self.mock_repo.update_last_login.assert_called_once_with("test_user")
        assert "test_user" in self.auth.logged_in_users

    def test_repository_update_failure(self):
        self.mock_repo.get_user.return_value = {"password": "valid_pass"}
        self.mock_repo.update_last_login.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception) as exc_info:
            self.auth.login("error_user", "valid_pass")
        assert "DB Error" in str(exc_info.value)
        assert "error_user" in self.auth.logged_in_users  # User added before failure

    def test_invalid_credentials_handling(self):
        self.mock_repo.get_user.return_value = {"password": "real_pass"}
        
        assert self.auth.login("user", "wrong_pass") is False
        assert "user" not in self.auth.logged_in_users
        self.mock_repo.update_last_login.assert_not_called()

    def test_nonexistent_user_login(self):
        self.mock_repo.get_user.return_value = None
        
        assert self.auth.login("ghost", "any_pass") is False
        self.mock_repo.update_last_login.assert_not_called()

    def test_edge_case_empty_username(self):
        self.mock_repo.get_user.return_value = None
        
        assert self.auth.login("", "pass") is False
        self.mock_repo.get_user.assert_called_once_with("")

    def test_real_integration_with_repository(self):
        real_repo = UserRepository()
        real_auth = AuthService(real_repo)
        
        assert real_auth.login("bob", "pass456") is True
        assert "bob" in real_auth.logged_in_users
        assert "last_login" in real_repo.users["bob"]