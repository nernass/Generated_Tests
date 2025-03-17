import pytest
from unittest.mock import MagicMock

class NotificationService:
    def __init__(self):
        self.notifications = []

    def notify(self, message):
        self.notifications.append(message)
        return len(self.notifications)

    def get_latest(self):
        return self.notifications[-1] if self.notifications else None

class TaskScheduler:
    def __init__(self, notification_service):
        self.tasks = {}
        self.notification_service = notification_service
        self.task_id_counter = 0

    def schedule_task(self, description, due_date):
        task_id = self.task_id_counter
        self.tasks[task_id] = {
            "description": description,
            "due_date": due_date,
            "completed": False
        }
        self.task_id_counter += 1
        self.notification_service.notify(f"New task scheduled: {description}")
        return task_id

    def complete_task(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id]["completed"] = True
            return True
        return False

@pytest.fixture
def notification_service():
    return NotificationService()

@pytest.fixture
def task_scheduler(notification_service):
    return TaskScheduler(notification_service)

class TestIntegrationNotificationServiceAndTaskScheduler:

    def test_success_path_schedule_and_complete_task(self, task_scheduler, notification_service):
        task_id = task_scheduler.schedule_task("Test Task", "2023-12-31")
        assert task_id == 0
        assert task_scheduler.tasks[task_id]["description"] == "Test Task"
        assert task_scheduler.tasks[task_id]["due_date"] == "2023-12-31"
        assert task_scheduler.tasks[task_id]["completed"] == False
        assert notification_service.get_latest() == "New task scheduled: Test Task"
        
        assert task_scheduler.complete_task(task_id) == True
        assert task_scheduler.tasks[task_id]["completed"] == True

    def test_partial_failure_notification_service_fails_on_schedule(self, task_scheduler, notification_service):
        notification_service.notify = MagicMock(side_effect=Exception("Notification failed"))
        with pytest.raises(Exception) as excinfo:
            task_scheduler.schedule_task("Test Task", "2023-12-31")
        assert str(excinfo.value) == "Notification failed"
        assert task_scheduler.tasks == {}

    def test_partial_failure_notification_service_fails_on_complete(self, task_scheduler, notification_service):
        task_id = task_scheduler.schedule_task("Test Task", "2023-12-31")
        notification_service.notify = MagicMock(side_effect=Exception("Notification failed"))
        with pytest.raises(Exception) as excinfo:
            task_scheduler.complete_task(task_id)
        assert str(excinfo.value) == "Notification failed"
        assert task_scheduler.tasks[task_id]["completed"] == False

    def test_edge_case_schedule_with_empty_description(self, task_scheduler, notification_service):
        task_id = task_scheduler.schedule_task("", "2023-12-31")
        assert task_id == 0
        assert task_scheduler.tasks[task_id]["description"] == ""
        assert task_scheduler.tasks[task_id]["due_date"] == "2023-12-31"
        assert task_scheduler.tasks[task_id]["completed"] == False
        assert notification_service.get_latest() == "New task scheduled: "

    def test_edge_case_complete_non_existent_task(self, task_scheduler, notification_service):
        assert task_scheduler.complete_task(999) == False
        assert notification_service.get_latest() is None