import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from NotificationService import NotificationService
from TaskScheduler import TaskScheduler

class TestTaskSchedulerIntegration:
    @pytest.fixture
    def mock_notification_service(self):
        return Mock(spec=NotificationService)

    @pytest.fixture
    def real_notification_service(self):
        return NotificationService()

    @pytest.fixture
    def task_scheduler_with_mock(self, mock_notification_service):
        return TaskScheduler(mock_notification_service)

    @pytest.fixture
    def task_scheduler_real(self, real_notification_service):
        return TaskScheduler(real_notification_service)

    # Success Path Tests
    def test_successful_task_scheduling(self, task_scheduler_with_mock, mock_notification_service):
        # Arrange
        task_desc = "Test Task"
        due_date = datetime.now() + timedelta(days=1)

        # Act
        task_id = task_scheduler_with_mock.schedule_task(task_desc, due_date)

        # Assert
        assert task_id == 0
        assert task_scheduler_with_mock.tasks[task_id]["description"] == task_desc
        assert task_scheduler_with_mock.tasks[task_id]["due_date"] == due_date
        mock_notification_service.notify.assert_called_once_with(f"New task scheduled: {task_desc}")

    def test_end_to_end_flow(self, task_scheduler_real, real_notification_service):
        # Arrange
        task_desc = "End to End Test"
        due_date = datetime.now() + timedelta(days=1)

        # Act
        task_id = task_scheduler_real.schedule_task(task_desc, due_date)
        task_scheduler_real.complete_task(task_id)

        # Assert
        assert task_scheduler_real.tasks[task_id]["completed"] == True
        assert len(real_notification_service.notifications) == 1
        assert real_notification_service.get_latest() == f"New task scheduled: {task_desc}"

    # Failure Path Tests
    def test_notification_service_failure(self, task_scheduler_with_mock, mock_notification_service):
        # Arrange
        mock_notification_service.notify.side_effect = Exception("Notification failed")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            task_scheduler_with_mock.schedule_task("Failed Task", datetime.now())
        assert str(exc_info.value) == "Notification failed"

    def test_invalid_task_completion(self, task_scheduler_real):
        # Act
        result = task_scheduler_real.complete_task(999)  # Non-existent task ID

        # Assert
        assert result == False

    # Edge Cases Tests
    def test_empty_task_description(self, task_scheduler_with_mock, mock_notification_service):
        # Arrange
        empty_desc = ""
        due_date = datetime.now()

        # Act
        task_id = task_scheduler_with_mock.schedule_task(empty_desc, due_date)

        # Assert
        assert task_scheduler_with_mock.tasks[task_id]["description"] == ""
        mock_notification_service.notify.assert_called_once_with("New task scheduled: ")

    def test_past_due_date(self, task_scheduler_with_mock, mock_notification_service):
        # Arrange
        past_date = datetime.now() - timedelta(days=7)

        # Act
        task_id = task_scheduler_with_mock.schedule_task("Past Task", past_date)

        # Assert
        assert task_scheduler_with_mock.tasks[task_id]["due_date"] == past_date

    def test_multiple_task_scheduling(self, task_scheduler_real, real_notification_service):
        # Arrange
        tasks = [
            ("Task 1", datetime.now()),
            ("Task 2", datetime.now() + timedelta(days=1)),
            ("Task 3", datetime.now() + timedelta(days=2))
        ]

        # Act
        task_ids = []
        for desc, date in tasks:
            task_ids.append(task_scheduler_real.schedule_task(desc, date))

        # Assert
        assert len(task_scheduler_real.tasks) == len(tasks)
        assert len(real_notification_service.notifications) == len(tasks)
        assert real_notification_service.get_latest() == f"New task scheduled: {tasks[-1][0]}"

    def test_notification_count_accuracy(self, task_scheduler_real, real_notification_service):
        # Act
        task_id_1 = task_scheduler_real.schedule_task("Task 1", datetime.now())
        task_id_2 = task_scheduler_real.schedule_task("Task 2", datetime.now())

        # Assert
        assert len(real_notification_service.notifications) == 2
        assert real_notification_service.notifications[0] == "New task scheduled: Task 1"
        assert real_notification_service.notifications[1] == "New task scheduled: Task 2"

    def test_data_flow_integrity(self, task_scheduler_with_mock, mock_notification_service):
        # Arrange
        test_tasks = [
            ("Task A", datetime.now()),
            ("Task B", datetime.now() + timedelta(days=1))
        ]

        # Act & Assert
        for desc, date in test_tasks:
            task_scheduler_with_mock.schedule_task(desc, date)
            mock_notification_service.notify.assert_called_with(f"New task scheduled: {desc}")