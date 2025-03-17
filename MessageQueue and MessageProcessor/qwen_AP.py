import pytest
from unittest.mock import MagicMock

class MessageProcessor:
    def __init__(self, queue):
        self.queue = queue
        self.processed_messages = []
        
    def process_next(self):
        message = self.queue.get_next_message()
        if message:
            self.processed_messages.append(message.upper())
            return True
        return False
        
    def process_all(self):
        count = 0
        while self.process_next():
            count += 1
        return count

class MessageQueue:
    def __init__(self):
        self.messages = []
        
    def add_message(self, message):
        self.messages.append(message)
        return True
        
    def get_next_message(self):
        if self.messages:
            return self.messages.pop(0)
        return None

@pytest.fixture
def message_queue():
    return MessageQueue()

@pytest.fixture
def message_processor(message_queue):
    return MessageProcessor(message_queue)

class TestIntegrationMessageProcessorAndMessageQueue:

    def test_success_path_process_next_single_message(self, message_processor, message_queue):
        message_queue.add_message("hello")
        result = message_processor.process_next()
        assert result == True
        assert message_processor.processed_messages == ["HELLO"]

    def test_success_path_process_all_multiple_messages(self, message_processor, message_queue):
        message_queue.add_message("hello")
        message_queue.add_message("world")
        message_queue.add_message("pytest")
        count = message_processor.process_all()
        assert count == 3
        assert message_processor.processed_messages == ["HELLO", "WORLD", "PYTEST"]

    def test_partial_failure_no_messages(self, message_processor, message_queue):
        result = message_processor.process_next()
        assert result == False
        assert message_processor.processed_messages == []

    def test_partial_failure_queue_throws_exception(self, message_processor, message_queue):
        message_queue.get_next_message = MagicMock(side_effect=Exception("Queue error"))
        with pytest.raises(Exception) as excinfo:
            message_processor.process_next()
        assert str(excinfo.value) == "Queue error"
        assert message_processor.processed_messages == []

    def test_edge_case_empty_string_message(self, message_processor, message_queue):
        message_queue.add_message("")
        result = message_processor.process_next()
        assert result == True
        assert message_processor.processed_messages == [""]

    def test_edge_case_long_message(self, message_processor, message_queue):
        long_message = "a" * 100
        message_queue.add_message(long_message)
        result = message_processor.process_next()
        assert result == True
        assert message_processor.processed_messages == [long_message.upper()]

    def test_edge_case_special_characters_message(self, message_processor, message_queue):
        special_message = "hello@world#123"
        message_queue.add_message(special_message)
        result = message_processor.process_next()
        assert result == True
        assert message_processor.processed_messages == [special_message.upper()]

    def test_edge_case_multiple_empty_messages(self, message_processor, message_queue):
        message_queue.add_message("")
        message_queue.add_message("")
        count = message_processor.process_all()
        assert count == 2
        assert message_processor.processed_messages == ["", ""]

    def test_edge_case_mixed_messages(self, message_processor, message_queue):
        message_queue.add_message("hello")
        message_queue.add_message("")
        message_queue.add_message("world")
        count = message_processor.process_all()
        assert count == 3
        assert message_processor.processed_messages == ["HELLO", "", "WORLD"]