import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
from TaskScheduler import TaskScheduler
from NotificationService import NotificationService

# Fixtures for dependency management
@pytest.fixture
def notification_service():
    return NotificationService()

@pytest.fixture
def mock_notification_service():
    mock = Mock(spec=NotificationService)
    mock.notify.return_value = 1  # Default return for first notification
    return mock

@pytest.fixture
def task_scheduler(notification_service):
    return TaskScheduler(notification_service)

@pytest.fixture
def task_scheduler_with_mock(mock_notification_service):
    return TaskScheduler(mock_notification_service)

# Success path tests
def test_schedule_task_end_to_end(task_scheduler, notification_service):
    """Test the full interaction between TaskScheduler and NotificationService"""
    # Arrange
    task_desc = "Integration Test Task"
    due_date = datetime.now() + timedelta(days=1)
    
    # Act
    task_id = task_scheduler.schedule_task(task_desc, due_date)
    
    # Assert - Task was scheduled correctly
    assert task_id == 0
    assert task_scheduler.tasks[task_id]["description"] == task_desc
    assert task_scheduler.tasks[task_id]["due_date"] == due_date
    assert task_scheduler.tasks[task_id]["completed"] == False
    
    # Assert - Notification was sent
    assert len(notification_service.notifications) == 1
    assert notification_service.notifications[0] == f"New task scheduled: {task_desc}"
    assert notification_service.get_latest() == f"New task scheduled: {task_desc}"

def test_multiple_task_scheduling(task_scheduler, notification_service):
    """Test multiple tasks being scheduled and tracked properly"""
    # Arrange
    tasks = [
        ("Task 1", datetime.now() + timedelta(days=1)),
        ("Task 2", datetime.now() + timedelta(days=2)),
        ("Task 3", datetime.now() + timedelta(days=3))
    ]
    
    # Act
    task_ids = []
    for desc, date in tasks:
        task_ids.append(task_scheduler.schedule_task(desc, date))
    
    # Assert - All tasks were scheduled
    assert len(task_scheduler.tasks) == len(tasks)
    for i, (desc, date) in enumerate(tasks):
        assert task_scheduler.tasks[i]["description"] == desc
        assert task_scheduler.tasks[i]["due_date"] == date
    
    # Assert - All notifications were sent in order
    assert len(notification_service.notifications) == len(tasks)
    for i, (desc, _) in enumerate(tasks):
        assert notification_service.notifications[i] == f"New task scheduled: {desc}"
    
    assert notification_service.get_latest() == f"New task scheduled: {tasks[-1][0]}"

# Failure path tests
def test_notification_service_exception(task_scheduler_with_mock, mock_notification_service):
    """Test behavior when NotificationService fails"""
    # Arrange
    mock_notification_service.notify.side_effect = Exception("Service unavailable")
    
    # Act/Assert - The scheduler should propagate the exception
    with pytest.raises(Exception, match="Service unavailable"):
        task_scheduler_with_mock.schedule_task("Task with error", datetime.now())

def test_complete_nonexistent_task(task_scheduler):
    """Test trying to complete a task that doesn't exist"""
    # Act
    result = task_scheduler.complete_task(999)  # Non-existent task ID
    
    # Assert
    assert result == False

# Edge case tests
def test_empty_task_description(task_scheduler, notification_service):
    """Test scheduling a task with an empty description"""
    # Arrange
    empty_desc = ""
    due_date = datetime.now() + timedelta(days=1)
    
    # Act
    task_id = task_scheduler.schedule_task(empty_desc, due_date)
    
    # Assert
    assert task_id == 0
    assert task_scheduler.tasks[task_id]["description"] == empty_desc
    assert notification_service.notifications[0] == "New task scheduled: "

def test_past_due_date(task_scheduler):
    """Test scheduling a task with a past due date"""
    # Arrange
    past_date = datetime.now() - timedelta(days=1)  # Date in the past
    
    # Act
    task_id = task_scheduler.schedule_task("Past due task", past_date)
    
    # Assert - Task should be scheduled regardless of past date
    assert task_id == 0
    assert task_scheduler.tasks[task_id]["due_date"] == past_date

def test_data_flow_verification(task_scheduler_with_mock, mock_notification_service):
    """Verify the data flow from TaskScheduler to NotificationService"""
    # Arrange
    task_desc = "Data Flow Test"
    due_date = datetime.now() + timedelta(days=1)
    
    # Act
    task_scheduler_with_mock.schedule_task(task_desc, due_date)
    
    # Assert - Verify the exact message passed to notify
    mock_notification_service.notify.assert_called_once_with(f"New task scheduled: {task_desc}")

def test_consecutive_notification_counts(notification_service):
    """Test that notification counts increment correctly"""
    # Act & Assert
    assert notification_service.notify("First") == 1
    assert notification_service.notify("Second") == 2
    assert notification_service.notify("Third") == 3

def test_get_latest_with_no_notifications(notification_service):
    """Test getting the latest notification when none exist"""
    # Assert
    assert notification_service.get_latest() is None

def test_notification_persistence_after_task_completion(task_scheduler, notification_service):
    """Test that notifications remain after tasks are completed"""
    # Arrange
    task_id = task_scheduler.schedule_task("Task to complete", datetime.now())
    initial_notification_count = len(notification_service.notifications)
    
    # Act
    task_scheduler.complete_task(task_id)
    
    # Assert
    assert len(notification_service.notifications) == initial_notification_count
    assert notification_service.get_latest() == "New task scheduled: Task to complete"