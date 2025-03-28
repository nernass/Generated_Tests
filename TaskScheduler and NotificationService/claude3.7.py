import pytest
from datetime import datetime
from NotificationService import NotificationService
from TaskScheduler import TaskScheduler

@pytest.fixture
def notification_service():
    return NotificationService()

@pytest.fixture
def task_scheduler(notification_service):
    return TaskScheduler(notification_service)

def test_task_scheduling_notification():
    # Setup
    notification_service = NotificationService()
    scheduler = TaskScheduler(notification_service)
    
    # Test task scheduling and notification
    task_desc = "Complete integration tests"
    due_date = datetime(2025, 12, 31)
    
    task_id = scheduler.schedule_task(task_desc, due_date)
    
    # Verify task was scheduled
    assert task_id == 0
    assert scheduler.tasks[task_id]["description"] == task_desc
    assert scheduler.tasks[task_id]["due_date"] == due_date
    
    # Verify notification was sent
    assert len(notification_service.notifications) == 1
    assert notification_service.notifications[0] == f"New task scheduled: {task_desc}"

def test_multiple_tasks_notifications():
    notification_service = NotificationService()
    scheduler = TaskScheduler(notification_service)
    
    # Schedule multiple tasks
    tasks = [
        ("Task 1", datetime(2025, 1, 1)),
        ("Task 2", datetime(2025, 1, 2)),
        ("Task 3", datetime(2025, 1, 3))
    ]
    
    for desc, date in tasks:
        scheduler.schedule_task(desc, date)
    
    # Verify notifications count and content
    assert len(notification_service.notifications) == len(tasks)
    for i, (desc, _) in enumerate(tasks):
        assert notification_service.notifications[i] == f"New task scheduled: {desc}"

def test_get_latest_notification():
    notification_service = NotificationService()
    scheduler = TaskScheduler(notification_service)
    
    # Schedule tasks and check latest notification
    scheduler.schedule_task("Task 1", datetime(2025, 1, 1))
    assert notification_service.get_latest() == "New task scheduled: Task 1"
    
    scheduler.schedule_task("Task 2", datetime(2025, 1, 2))
    assert notification_service.get_latest() == "New task scheduled: Task 2"
    
def test_complete_task():
    notification_service = NotificationService()
    scheduler = TaskScheduler(notification_service)
    
    # Schedule and complete a task
    task_id = scheduler.schedule_task("Test task", datetime(2025, 1, 1))
    
    assert scheduler.complete_task(task_id) == True
    assert scheduler.tasks[task_id]["completed"] == True
    
    # Verify invalid task completion
    assert scheduler.complete_task(999) == False

def test_empty_notification_service():
    notification_service = NotificationService()
    
    # Check behavior with no notifications
    assert notification_service.get_latest() is None

def test_notification_count():
    notification_service = NotificationService()
    scheduler = TaskScheduler(notification_service)
    
    # Verify notification count is returned correctly
    count = scheduler.notification_service.notify("Test message")
    assert count == 1
    
    count = scheduler.notification_service.notify("Another message")
    assert count == 2