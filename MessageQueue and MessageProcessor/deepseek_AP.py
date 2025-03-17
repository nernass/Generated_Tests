import pytest
from unittest.mock import MagicMock
from MessageProcessor import MessageProcessor
from MessageQueue import MessageQueue

class TestIntegrationMessageProcessor:
    def setup_method(self):
        self.mock_queue = MagicMock(spec=MessageQueue)
        self.processor = MessageProcessor(self.mock_queue)

    def test_successful_message_processing(self):
        self.mock_queue.get_next_message.return_value = "valid_message"
        
        result = self.processor.process_next()
        
        assert result is True
        assert "VALID_MESSAGE" in self.processor.processed_messages
        self.mock_queue.get_next_message.assert_called_once()

    def test_process_all_messages_flow(self):
        self.mock_queue.get_next_message.side_effect = ["msg1", "msg2", None]
        
        count = self.processor.process_all()
        
        assert count == 2
        assert self.mock_queue.get_next_message.call_count == 3
        assert self.processor.processed_messages == ["MSG1", "MSG2"]

    def test_empty_queue_handling(self):
        self.mock_queue.get_next_message.return_value = None
        
        assert self.processor.process_next() is False
        assert len(self.processor.processed_messages) == 0

    def test_queue_failure_propagation(self):
        self.mock_queue.get_next_message.side_effect = RuntimeError("Queue read error")
        
        with pytest.raises(RuntimeError) as exc_info:
            self.processor.process_next()
        assert "Queue read error" in str(exc_info.value)

    def test_edge_case_large_message(self):
        self.mock_queue.get_next_message.return_value = "x" * 1000
        
        self.processor.process_next()
        assert ("X" * 1000) in self.processor.processed_messages

    def test_real_integration_end_to_end(self):
        real_queue = MessageQueue()
        real_queue.add_message("test1")
        real_queue.add_message("test2")
        processor = MessageProcessor(real_queue)
        
        assert processor.process_all() == 2
        assert processor.processed_messages == ["TEST1", "TEST2"]