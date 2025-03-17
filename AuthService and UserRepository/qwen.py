import pytest
from unittest.mock import MagicMock

class AuthService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
        self.logged_in_users = []
        
    def login(self, username, password):
        user = self.user_repository.get_user(username)
        if user and user["password"] == password:
            self.logged_in_users.append(username)
            self.user_repository.update_last_login(username)
            return True
        return False

class UserRepository:
    def __init__(self):
        self.users = {
            "alice": {"password": "pass123", "role": "admin"},
            "bob": {"password": "pass456", "role": "user"}
        }
        
    def get_user(self, username):
        return self.users.get(username)
        
    def update_last_login(self, username):
        if username in self.users:
            self.users[username]["last_login"] = "2023-07-14"
            return True
        return False

@pytest.fixture
def user_repository():
    return UserRepository()

@pytest.fixture
def auth_service(user_repository):
    return AuthService(user_repository)

class TestIntegrationAuthServiceAndUserRepository:

    def test_success_path_login_with_valid_credentials(self, auth_service, user_repository):
        result = auth_service.login("alice", "pass123")
        assert result == True
        assert "alice" in auth_service.logged_in_users
        assert user_repository.users["alice"]["last_login"] == "2023-07-14"

    def test_partial_failure_login_with_invalid_password(self, auth_service, user_repository):
        result = auth_service.login("alice", "wrongpass")
        assert result == False
        assert "alice" not in auth_service.logged_in_users
        assert "last_login" not in user_repository.users["alice"]

    def test_partial_failure_login_with_nonexistent_user(self, auth_service, user_repository):
        result = auth_service.login("nonexistent", "pass123")
        assert result == False
        assert "nonexistent" not in auth_service.logged_in_users

    def test_partial_failure_update_last_login_fails(self, auth_service, user_repository):
        user_repository.update_last_login = MagicMock(return_value=False)
        result = auth_service.login("alice", "pass123")
        assert result == False
        assert "alice" not in auth_service.logged_in_users

    def test_edge_case_login_with_empty_username(self, auth_service, user_repository):
        result = auth_service.login("", "pass123")
        assert result == False
        assert "" not in auth_service.logged_in_users

    def test_edge_case_login_with_empty_password(self, auth_service, user_repository):
        result = auth_service.login("alice", "")
        assert result == False
        assert "alice" not in auth_service.logged_in_users

    def test_edge_case_login_with_long_username(self, auth_service, user_repository):
        long_username = "a" * 100
        result = auth_service.login(long_username, "pass123")
        assert result == False
        assert long_username not in auth_service.logged_in_users

    def test_edge_case_login_with_long_password(self, auth_service, user_repository):
        long_password = "p" * 100
        result = auth_service.login("alice", long_password)
        assert result == False
        assert "alice" not in auth_service.logged_in_users