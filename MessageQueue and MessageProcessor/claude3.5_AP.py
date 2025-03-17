import pytest
import logging
from unittest.mock import MagicMock, patch
from MessageQueue import MessageQueue
from MessageProcessor import MessageProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMessageIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.queue = MessageQueue()
        self.processor = MessageProcessor(self.queue)
        logger.info("Test setup complete")
        yield
        logger.info("Test cleanup complete")

    @pytest.fixture
    def mock_queue(self):
        return MagicMock(spec=MessageQueue)

    def test_success_path(self):
        # Test complete workflow with valid messages
        test_messages = ["test1", "test2", "test3"]
        for msg in test_messages:
            self.queue.add_message(msg)
        
        count = self.processor.process_all()
        
        assert count == 3
        assert self.processor.processed_messages == ["TEST1", "TEST2", "TEST3"]
        assert len(self.queue.messages) == 0
        logger.info("Success path test completed")

    def test_component_failure(self, mock_queue):
        # Test failure in queue component
        processor = MessageProcessor(mock_queue)
        mock_queue.get_next_message.side_effect = ConnectionError("Queue failure")
        
        with pytest.raises(ConnectionError) as exc_info:
            processor.process_next()
        
        assert str(exc_info.value) == "Queue failure"
        assert len(processor.processed_messages) == 0
        logger.info("Component failure test completed")

    def test_invalid_input(self):
        # Test handling of invalid inputs
        invalid_inputs = [None, 123, {"key": "value"}]
        
        for invalid_input in invalid_inputs:
            self.queue.add_message(invalid_input)
            with pytest.raises((AttributeError, TypeError)):
                self.processor.process_next()
        
        assert len(self.processor.processed_messages) == 0
        logger.info("Invalid input test completed")

    def test_edge_cases(self):
        # Test boundary conditions
        edge_cases = ["", " ", "a" * 1000000]
        
        for case in edge_cases:
            self.queue.add_message(case)
            assert self.processor.process_next() == True
        
        assert len(self.processor.processed_messages) == len(edge_cases)
        assert self.processor.processed_messages[0] == ""
        assert self.processor.processed_messages[1] == " "
        assert len(self.processor.processed_messages[2]) == 1000000
        logger.info("Edge cases test completed")

    def test_concurrent_operations(self):
        # Test interleaved operations
        self.queue.add_message("first")
        assert self.processor.process_next() == True
        
        self.queue.add_message("second")
        self.queue.add_message("third")
        count = self.processor.process_all()
        
        assert count == 2
        assert self.processor.processed_messages == ["FIRST", "SECOND", "THIRD"]
        logger.info("Concurrent operations test completed")

    @pytest.mark.parametrize("batch_size", [10, 100, 1000])
    def test_performance(self, batch_size):
        # Test performance with different batch sizes
        for i in range(batch_size):
            self.queue.add_message(f"msg{i}")
        
        count = self.processor.process_all()
        
        assert count == batch_size
        assert len(self.processor.processed_messages) == batch_size
        logger.info(f"Performance test completed with batch size {batch_size}")

    def test_recovery_behavior(self, mock_queue):
        # Test system recovery after failures
        processor = MessageProcessor(mock_queue)
        mock_queue.get_next_message.side_effect = [
            "message1",
            ConnectionError("Temporary failure"),
            "message2"
        ]
        
        # First message should succeed
        assert processor.process_next() == True
        
        # Second should fail
        with pytest.raises(ConnectionError):
            processor.process_next()
        
        # Third should succeed after recovery
        mock_queue.get_next_message.side_effect = ["message2"]
        assert processor.process_next() == True
        
        assert processor.processed_messages == ["MESSAGE1", "MESSAGE2"]
        logger.info("Recovery behavior test completed")