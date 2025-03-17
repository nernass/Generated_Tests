import pytest
from unittest.mock import MagicMock
from MessageQueue import MessageQueue
from MessageProcessor import MessageProcessor

@pytest.fixture
def setup_environment():
    queue = MessageQueue()
    processor = MessageProcessor(queue)
    return queue, processor

def test_success_path(setup_environment):
    queue, processor = setup_environment
    
    # Test empty queue
    assert processor.process_next() == False
    assert len(processor.processed_messages) == 0
    
    # Test single message processing
    queue.add_message("test")
    assert processor.process_next() == True
    assert processor.processed_messages == ["TEST"]
    assert queue.get_next_message() == None
    
    # Test multiple message processing
    test_messages = ["hello", "world", "python"]
    for msg in test_messages:
        queue.add_message(msg)
    
    process_count = processor.process_all()
    assert process_count == 3
    assert processor.processed_messages == ["TEST", "HELLO", "WORLD", "PYTHON"]
    assert len(queue.messages) == 0

def test_partial_failure(setup_environment):
    queue, processor = setup_environment
    
    # Mock get_next_message to raise an exception
    queue.get_next_message = MagicMock(side_effect=Exception("Mocked exception"))
    
    with pytest.raises(Exception, match="Mocked exception"):
        processor.process_next()
    
    assert len(processor.processed_messages) == 0

def test_edge_case_handling(setup_environment):
    queue, processor = setup_environment
    
    # Test with None message
    queue.add_message(None)
    with pytest.raises(AttributeError):
        processor.process_next()
    
    # Reset and test with non-string message
    queue.messages = [42]
    with pytest.raises(AttributeError):
        processor.process_next()
    
    # Test with empty string
    queue.messages = [""]
    assert processor.process_next() == True
    assert processor.processed_messages == [""]
    
    # Test with large input
    large_message = "a" * 10000
    queue.add_message(large_message)
    assert processor.process_next() == True
    assert processor.processed_messages[-1] == large_message.upper()