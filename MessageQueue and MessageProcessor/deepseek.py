import pytest
from unittest.mock import MagicMock
from MessageProcessor import MessageProcessor
from MessageQueue import MessageQueue

class TestIntegrationMessageProcessor:
    def setup_method(self):
        self.mock_queue = MagicMock(spec=MessageQueue)
        self.processor = MessageProcessor(self.mock_queue)

    def test_successful_message_processing(self):
        self.mock_queue.get_next_message.return_value = "test_message"
        
        result = self.processor.process_next()
        
        assert result is True
        assert "TEST_MESSAGE" in self.processor.processed_messages
        self.mock_queue.get_next_message.assert_called_once()

    def test_process_all_messages(self):
        self.mock_queue.get_next_message.side_effect = ["msg1", "msg2", None]
        
        count = self.processor.process_all()
        
        assert count == 2
        assert len(self.processor.processed_messages) == 2
        assert self.mock_queue.get_next_message.call_count == 3

    def test_empty_queue_handling(self):
        self.mock_queue.get_next_message.return_value = None
        
        assert self.processor.process_next() is False
        assert len(self.processor.processed_messages) == 0

    def test_queue_failure_propagation(self):
        self.mock_queue.get_next_message.side_effect = RuntimeError("Queue error")
        
        with pytest.raises(RuntimeError) as exc_info:
            self.processor.process_next()
        assert "Queue error" in str(exc_info.value)

    def test_real_integration_flow(self):
        real_queue = MessageQueue()
        real_queue.add_message("hello")
        real_queue.add_message("world")
        processor = MessageProcessor(real_queue)
        
        assert processor.process_all() == 2
        assert processor.processed_messages == ["HELLO", "WORLD"]