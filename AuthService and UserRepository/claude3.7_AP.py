import pytest
from unittest.mock import Mock, patch
from AuthService import AuthService
from UserRepository import UserRepository

# ----------------------------------------
# Test fixtures for setup
# ----------------------------------------

@pytest.fixture
def user_repository():
    """Create a real UserRepository instance."""
    return UserRepository()

@pytest.fixture
def auth_service(user_repository):
    """Create AuthService with a real UserRepository."""
    return AuthService(user_repository)

@pytest.fixture
def mocked_user_repository():
    """Create a mocked UserRepository for testing failures."""
    mock_repo = Mock(spec=UserRepository)
    # Set up default behavior
    mock_repo.get_user.side_effect = lambda username: (
        {"password": "pass123", "role": "admin"} if username == "alice" else
        {"password": "pass456", "role": "user"} if username == "bob" else
        None
    )
    mock_repo.update_last_login.return_value = True
    return mock_repo

@pytest.fixture
def auth_service_with_mock(mocked_user_repository):
    """Create AuthService with a mocked UserRepository."""
    return AuthService(mocked_user_repository)

# ----------------------------------------
# Success path tests
# ----------------------------------------

def test_successful_login_flow(auth_service, user_repository):
    """Test the success path of login flow."""
    # Execute the workflow
    result = auth_service.login("alice", "pass123")
    
    # Assert final output
    assert result == True
    assert "alice" in auth_service.logged_in_users
    
    # Verify side effects
    user = user_repository.get_user("alice")
    assert "last_login" in user
    assert user["last_login"] == "2023-07-14"

def test_multiple_successful_logins(auth_service):
    """Test multiple users can log in successfully."""
    # Execute the workflow for multiple users
    result1 = auth_service.login("alice", "pass123")
    result2 = auth_service.login("bob", "pass456")
    
    # Assert final outputs
    assert result1 == True
    assert result2 == True
    assert "alice" in auth_service.logged_in_users
    assert "bob" in auth_service.logged_in_users
    assert len(auth_service.logged_in_users) == 2

# ----------------------------------------
# Data flow accuracy tests
# ----------------------------------------

def test_auth_service_passes_correct_username_to_repository(auth_service_with_mock, mocked_user_repository):
    """Test that AuthService passes the correct username to UserRepository."""
    # Execute the workflow
    auth_service_with_mock.login("alice", "pass123")
    
    # Verify data flow accuracy
    mocked_user_repository.get_user.assert_called_once_with("alice")
    mocked_user_repository.update_last_login.assert_called_once_with("alice")

# ----------------------------------------
# Partial failure tests
# ----------------------------------------

def test_repository_get_user_failure(auth_service_with_mock, mocked_user_repository):
    """Test handling of get_user method failing."""
    # Force get_user to fail
    mocked_user_repository.get_user.return_value = None
    
    # Execute the workflow
    result = auth_service_with_mock.login("alice", "pass123")
    
    # Verify AuthService handles the failure
    assert result == False
    assert "alice" not in auth_service_with_mock.logged_in_users
    mocked_user_repository.update_last_login.assert_not_called()

def test_repository_update_last_login_failure(auth_service_with_mock, mocked_user_repository):
    """Test handling of update_last_login method failing."""
    # Set up the mocks
    mocked_user_repository.update_last_login.return_value = False
    
    # Execute the workflow
    result = auth_service_with_mock.login("alice", "pass123")
    
    # AuthService doesn't check update_last_login's return value in current implementation
    # so the login will still succeed
    assert result == True
    assert "alice" in auth_service_with_mock.logged_in_users
    mocked_user_repository.update_last_login.assert_called_once_with("alice")

def test_repository_update_last_login_exception(auth_service_with_mock, mocked_user_repository):
    """Test handling of update_last_login method throwing exception."""
    # Force update_last_login to throw exception
    mocked_user_repository.update_last_login.side_effect = Exception("Database error")
    
    # Execute the workflow and verify exception is propagated
    with pytest.raises(Exception, match="Database error"):
        auth_service_with_mock.login("alice", "pass123")
    
    # Verify partial execution before exception
    mocked_user_repository.get_user.assert_called_once_with("alice")
    assert "alice" not in auth_service_with_mock.logged_in_users

# ----------------------------------------
# Edge case tests
# ----------------------------------------

def test_login_with_empty_username(auth_service):
    """Test login with empty username."""
    result = auth_service.login("", "pass123")
    assert result == False
    assert "" not in auth_service.logged_in_users

def test_login_with_empty_password(auth_service):
    """Test login with empty password."""
    result = auth_service.login("alice", "")
    assert result == False
    assert "alice" not in auth_service.logged_in_users

def test_login_with_none_values(auth_service):
    """Test login with None username or password."""
    result1 = auth_service.login(None, "pass123")
    result2 = auth_service.login("alice", None)
    assert result1 == False
    assert result2 == False
    assert None not in auth_service.logged_in_users
    assert "alice" not in auth_service.logged_in_users

def test_login_with_extra_long_values(auth_service_with_mock, mocked_user_repository):
    """Test login with extremely long username or password."""
    long_string = "x" * 10000
    
    # Set up mock to handle long username
    mocked_user_repository.get_user.return_value = {"password": "pass123"}
    
    # Execute workflow with long username
    result1 = auth_service_with_mock.login(long_string, "pass123")
    
    # Execute workflow with long password
    mocked_user_repository.get_user.return_value = {"password": long_string}
    result2 = auth_service_with_mock.login("alice", long_string)
    
    # Verify results
    assert result1 == False  # Long username doesn't exist in real repo
    assert result2 == True   # Login should succeed with long password