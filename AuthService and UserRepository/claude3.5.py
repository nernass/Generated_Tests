import pytest
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
    # Test multiple user login tracking
    auth_service.login("alice", "pass123")
    auth_service.login("bob", "pass456")
    assert set(auth_service.logged_in_users) == {"alice", "bob"}

def test_failed_login_no_state_change(auth_service, user_repository):
    # Test that failed login doesn't modify state
    original_user = user_repository.get_user("alice").copy()
    auth_service.login("alice", "wrongpass")
    current_user = user_repository.get_user("alice")
    assert "last_login" not in current_user
    assert current_user == original_user