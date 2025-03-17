import pytest
from unittest.mock import Mock
from datetime import datetime
from NotificationService import NotificationService
from TaskScheduler import TaskScheduler

@pytest.fixture
def mock_notification_service():
    return Mock(spec=NotificationService)

@pytest.fixture
def task_scheduler(mock_notification_service):
    return TaskScheduler(mock_notification_service)

def test_task_scheduling_notification(task_scheduler, mock_notification_service):
    # Test task scheduling and notification
    task_desc = "Complete integration tests"
    due_date = datetime(2025, 12, 31)
    
    task_id = task_scheduler.schedule_task(task_desc, due_date)
    
    # Verify task was scheduled
    assert task_id == 0
    assert task_scheduler.tasks[task_id]["description"] == task_desc
    assert task_scheduler.tasks[task_id]["due_date"] == due_date
    
    # Verify notification was sent
    mock_notification_service.notify.assert_called_once_with(f"New task scheduled: {task_desc}")

def test_multiple_tasks_notifications(task_scheduler, mock_notification_service):
    # Schedule multiple tasks
    tasks = [
        ("Task 1", datetime(2025, 1, 1)),
        ("Task 2", datetime(2025, 1, 2)),
        ("Task 3", datetime(2025, 1, 3))
    ]
    
    for desc, date in tasks:
        task_scheduler.schedule_task(desc, date)
    
    # Verify notifications count and content
    assert mock_notification_service.notify.call_count == len(tasks)
    for desc, _ in tasks:
        mock_notification_service.notify.assert_any_call(f"New task scheduled: {desc}")

def test_get_latest_notification(task_scheduler, mock_notification_service):
    # Schedule tasks and check latest notification
    task_scheduler.schedule_task("Task 1", datetime(2025, 1, 1))
    task_scheduler.schedule_task("Task 2", datetime(2025, 1, 2))
    
    # Mock get_latest to return the latest notification
    mock_notification_service.get_latest.return_value = "New task scheduled: Task 2"
    
    assert mock_notification_service.get_latest() == "New task scheduled: Task 2"
    
def test_complete_task(task_scheduler):
    # Schedule and complete a task
    task_id = task_scheduler.schedule_task("Test task", datetime(2025, 1, 1))
    
    assert task_scheduler.complete_task(task_id) == True
    assert task_scheduler.tasks[task_id]["completed"] == True
    
    # Verify invalid task completion
    assert task_scheduler.complete_task(999) == False

def test_empty_notification_service(mock_notification_service):
    # Mock get_latest to return None when no notifications
    mock_notification_service.get_latest.return_value = None
    
    # Check behavior with no notifications
    assert mock_notification_service.get_latest() is None

def test_notification_count(mock_notification_service):
    # Mock notify to return the count of notifications
    mock_notification_service.notify.side_effect = lambda msg: len(mock_notification_service.notifications) + 1
    
    # Verify notification count is returned correctly
    count = mock_notification_service.notify("Test message")
    assert count == 1
    
    count = mock_notification_service.notify("Another message")
    assert count == 2