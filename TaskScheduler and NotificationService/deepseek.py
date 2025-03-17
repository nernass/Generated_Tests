import pytest
from unittest.mock import MagicMock
from NotificationService import NotificationService
from TaskScheduler import TaskScheduler

class TestIntegrationTaskScheduler:
    def setup_method(self):
        self.mock_notifier = MagicMock(spec=NotificationService)
        self.scheduler = TaskScheduler(self.mock_notifier)

    def test_task_scheduling_notification(self):
        self.mock_notifier.notify.return_value = 1
        task_id = self.scheduler.schedule_task("Project Meeting", "2023-10-05")
        
        assert isinstance(task_id, int)
        self.mock_notifier.notify.assert_called_once_with("New task scheduled: Project Meeting")
        assert self.scheduler.tasks[task_id]["description"] == "Project Meeting"

    def test_multiple_task_notifications(self):
        self.mock_notifier.notify.side_effect = [1, 2]
        
        id1 = self.scheduler.schedule_task("Code Review", "2023-10-06")
        id2 = self.scheduler.schedule_task("Documentation", "2023-10-07")
        
        assert id2 == id1 + 1
        assert self.mock_notifier.notify.call_count == 2

    def test_complete_task_flow(self):
        task_id = self.scheduler.schedule_task("Testing", "2023-10-08")
        assert self.scheduler.complete_task(task_id) is True
        assert self.scheduler.tasks[task_id]["completed"] is True

    def test_complete_invalid_task(self):
        assert self.scheduler.complete_task(999) is False

    def test_real_notification_integration(self):
        real_notifier = NotificationService()
        real_scheduler = TaskScheduler(real_notifier)
        
        task_id = real_scheduler.schedule_task("Deployment", "2023-10-09")
        assert real_notifier.get_latest() == "New task scheduled: Deployment"
        assert real_notifier.notifications == ["New task scheduled: Deployment"]