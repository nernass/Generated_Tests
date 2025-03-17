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
    assert notification_service.get_latest() == f"New task scheduled: {task_desc}"

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
    
    # Verify notifications
    assert len(notification_service.notifications) == len(tasks)
    assert notification_service.get_latest() == f"New task scheduled: {tasks[-1][0]}"

def test_complete_task_state():
    notification_service = NotificationService()
    scheduler = TaskScheduler(notification_service)
    
    # Schedule and complete a task
    task_id = scheduler.schedule_task("Test task", datetime(2025, 1, 1))
    
    assert scheduler.complete_task(task_id) == True
    assert scheduler.tasks[task_id]["completed"] == True
    
    # Verify invalid task completion
    assert scheduler.complete_task(999) == False

def test_notification_persistence():
    notification_service = NotificationService()
    scheduler = TaskScheduler(notification_service)
    
    # Schedule tasks and verify notifications persist
    task1_id = scheduler.schedule_task("Task 1", datetime(2025, 1, 1))
    task2_id = scheduler.schedule_task("Task 2", datetime(2025, 1, 2))
    
    assert len(notification_service.notifications) == 2
    assert notification_service.notifications[0] == "New task scheduled: Task 1"
    assert notification_service.notifications[1] == "New task scheduled: Task 2"