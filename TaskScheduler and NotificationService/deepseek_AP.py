import pytest
from unittest.mock import MagicMock
from NotificationService import NotificationService
from TaskScheduler import TaskScheduler

class TestIntegrationTaskScheduler:
    def setup_method(self):
        self.mock_notifier = MagicMock(spec=NotificationService)
        self.scheduler = TaskScheduler(self.mock_notifier)

    def test_successful_task_scheduling(self):
        self.mock_notifier.notify.return_value = 1
        task_id = self.scheduler.schedule_task("Code Review", "2023-10-10")
        
        assert task_id == 0
        self.mock_notifier.notify.assert_called_once_with("New task scheduled: Code Review")
        assert self.scheduler.tasks[task_id]["due_date"] == "2023-10-10"

    def test_notification_failure_propagation(self):
        self.mock_notifier.notify.side_effect = RuntimeError("Notification failed")
        with pytest.raises(RuntimeError) as exc_info:
            self.scheduler.schedule_task("Invalid Task", "")
        assert "Notification failed" in str(exc_info.value)
        assert len(self.scheduler.tasks) == 0

    def test_multiple_task_ids_and_notifications(self):
        self.mock_notifier.notify.side_effect = [1, 2, 3]
        
        id0 = self.scheduler.schedule_task("T1", "2023-10-11")
        id1 = self.scheduler.schedule_task("T2", "2023-10-12")
        
        assert id1 == id0 + 1
        assert self.mock_notifier.notify.call_count == 2
        assert "T2" in self.mock_notifier.notify.call_args_list[1].args[0]

    def test_complete_valid_and_invalid_tasks(self):
        task_id = self.scheduler.schedule_task("Valid Task", "2023-10-13")
        assert self.scheduler.complete_task(task_id) is True
        assert self.scheduler.complete_task(9999) is False

    def test_edge_case_empty_description(self):
        self.mock_notifier.notify.return_value = 1
        task_id = self.scheduler.schedule_task("", "2023-10-14")
        assert self.mock_notifier.notify.called_with("New task scheduled: ")

    def test_real_integration_flow(self):
        real_notifier = NotificationService()
        real_scheduler = TaskScheduler(real_notifier)
        
        real_scheduler.schedule_task("Production Deploy", "2023-10-15")
        assert real_notifier.get_latest() == "New task scheduled: Production Deploy"
        assert real_notifier.notifications == ["New task scheduled: Production Deploy"]