import pytest
from unittest.mock import Mock, patch
from AuthService import AuthService
from UserRepository import UserRepository

@pytest.fixture
def user_repository():
    return UserRepository()

@pytest.fixture
def auth_service(user_repository):
    return AuthService(user_repository)

def test_successful_login_integration(auth_service):
    # Test successful login flow
    assert auth_service.login("alice", "pass123") == True
    assert "alice" in auth_service.logged_in_users

def test_failed_login_integration(auth_service):
    # Test failed login with wrong password
    assert auth_service.login("alice", "wrongpass") == False
    assert "alice" not in auth_service.logged_in_users

def test_nonexistent_user_login_integration(auth_service):
    # Test login with non-existent user
    assert auth_service.login("carol", "pass123") == False
    assert "carol" not in auth_service.logged_in_users

def test_last_login_update_integration(auth_service, user_repository):
    # Test last login timestamp update
    auth_service.login("bob", "pass456")
    user = user_repository.get_user("bob")
    assert "last_login" in user
    assert user["last_login"] == "2023-07-14"

def test_multiple_user_logins_integration(auth_service):
    # Test multiple user logins
    auth_service.login("alice", "pass123")
    auth_service.login("bob", "pass456")
    assert "alice" in auth_service.logged_in_users
    assert "bob" in auth_service.logged_in_users
    assert len(auth_service.logged_in_users) == 2

def test_login_updates_repository_state(auth_service, user_repository):
    # Test that repository state is updated after login
    before_login = "last_login" in user_repository.get_user("alice")
    auth_service.login("alice", "pass123")
    after_login = "last_login" in user_repository.get_user("alice")
    assert before_login == False
    assert after_login == True

def test_failed_login_preserves_repository_state(auth_service, user_repository):
    # Test that repository state is preserved after failed login
    user_repository.get_user("alice").pop("last_login", None)
    auth_service.login("alice", "wrongpass")
    assert "last_login" not in user_repository.get_user("alice")

def test_partial_failure_handling(auth_service):
    # Mock the update_last_login method to simulate a failure
    with patch.object(UserRepository, 'update_last_login', return_value=False):
        assert auth_service.login("alice", "pass123") == False
        assert "alice" not in auth_service.logged_in_users

def test_edge_case_empty_username(auth_service):
    # Test login with empty username
    assert auth_service.login("", "pass123") == False

def test_edge_case_empty_password(auth_service):
    # Test login with empty password
    assert auth_service.login("alice", "") == False