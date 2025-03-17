import pytest
from unittest.mock import MagicMock, patch
from MessageQueue import MessageQueue
from MessageProcessor import MessageProcessor

@pytest.fixture
def mock_queue():
    return MagicMock(spec=MessageQueue)

@pytest.fixture
def real_queue():
    return MessageQueue()

@pytest.fixture
def processor_with_mock_queue(mock_queue):
    return MessageProcessor(mock_queue)

@pytest.fixture
def real_setup():
    queue = MessageQueue()
    processor = MessageProcessor(queue)
    return queue, processor

# Success path tests - using real components
def test_success_path_end_to_end(real_setup):
    queue, processor = real_setup
    
    # Test with multiple messages
    test_messages = ["hello", "world", "python"]
    for msg in test_messages:
        queue.add_message(msg)
    
    # Process all messages
    count = processor.process_all()
    
    # Validate results
    assert count == 3
    assert processor.processed_messages == ["HELLO", "WORLD", "PYTHON"]
    assert len(queue.messages) == 0

# Component interaction tests - using mocks
def test_processor_calls_queue_correctly(mock_queue, processor_with_mock_queue):
    # Setup mock behavior
    mock_queue.get_next_message.side_effect = ["test1", "test2", None]
    
    # Execute processor methods
    result1 = processor_with_mock_queue.process_next()
    result2 = processor_with_mock_queue.process_next()
    result3 = processor_with_mock_queue.process_next()
    
    # Verify interactions
    assert mock_queue.get_next_message.call_count == 3
    assert result1 == True
    assert result2 == True
    assert result3 == False
    assert processor_with_mock_queue.processed_messages == ["TEST1", "TEST2"]

def test_process_all_interaction(mock_queue, processor_with_mock_queue):
    # Setup mock behavior
    mock_queue.get_next_message.side_effect = ["message1", "message2", None]
    
    # Execute process_all
    count = processor_with_mock_queue.process_all()
    
    # Verify interactions
    assert mock_queue.get_next_message.call_count == 3
    assert count == 2
    assert processor_with_mock_queue.processed_messages == ["MESSAGE1", "MESSAGE2"]

# Failure path tests
def test_queue_exception_propagation(mock_queue, processor_with_mock_queue):
    # Force queue to raise exception
    mock_queue.get_next_message.side_effect = ConnectionError("Database connection failed")
    
    # Verify exception propagates through processor
    with pytest.raises(ConnectionError, match="Database connection failed"):
        processor_with_mock_queue.process_next()

def test_message_processing_exception(real_setup):
    queue, processor = real_setup
    
    # Add a non-string message that will cause upper() to fail
    queue.add_message(None)
    
    # Verify exception is raised
    with pytest.raises(AttributeError):
        processor.process_next()

# Edge case tests
def test_empty_queue(real_setup):
    queue, processor = real_setup
    
    # Test with empty queue
    result = processor.process_next()
    assert result == False
    assert len(processor.processed_messages) == 0
    
    count = processor.process_all()
    assert count == 0
    assert len(processor.processed_messages) == 0

def test_empty_string_message(real_setup):
    queue, processor = real_setup
    
    # Add empty string
    queue.add_message("")
    
    # Process and verify
    result = processor.process_next()
    assert result == True
    assert processor.processed_messages == [""]

def test_large_message(real_setup):
    queue, processor = real_setup
    
    # Create a very large message
    large_message = "a" * 100000
    queue.add_message(large_message)
    
    # Process and verify
    result = processor.process_next()
    assert result == True
    assert processor.processed_messages == [large_message.upper()]
    assert len(processor.processed_messages[0]) == 100000

def test_special_characters(real_setup):
    queue, processor = real_setup
    
    # Test with special characters
    special_msg = "Hello! @#$%^&*()_+{}[]"
    queue.add_message(special_msg)
    
    result = processor.process_next()
    assert result == True
    assert processor.processed_messages == [special_msg.upper()]

# Performance test
def test_many_messages_performance(real_setup):
    queue, processor = real_setup
    
    # Add many messages
    for i in range(1000):
        queue.add_message(f"message{i}")
    
    # Process all and verify count
    count = processor.process_all()
    assert count == 1000
    assert len(processor.processed_messages) == 1000
    assert processor.processed_messages[0] == "MESSAGE0"
    assert processor.processed_messages[-1] == "MESSAGE999"