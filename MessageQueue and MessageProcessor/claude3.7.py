import pytest
from MessageQueue import MessageQueue
from MessageProcessor import MessageProcessor

def test_message_flow():
    # Setup
    queue = MessageQueue()
    processor = MessageProcessor(queue)
    
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

def test_message_ordering():
    queue = MessageQueue()
    processor = MessageProcessor(queue)
    
    messages = ["first", "second", "third"]
    for msg in messages:
        queue.add_message(msg)
    
    processor.process_all()
    assert processor.processed_messages == ["FIRST", "SECOND", "THIRD"]

def test_empty_processing():
    queue = MessageQueue()
    processor = MessageProcessor(queue)
    
    assert processor.process_all() == 0
    assert len(processor.processed_messages) == 0

def test_interleaved_operations():
    queue = MessageQueue()
    processor = MessageProcessor(queue)
    
    queue.add_message("one")
    assert processor.process_next() == True
    
    queue.add_message("two")
    queue.add_message("three")
    assert processor.process_all() == 2
    
    assert processor.processed_messages == ["ONE", "TWO", "THREE"]

def test_error_handling():
    queue = MessageQueue()
    processor = MessageProcessor(queue)
    
    # Test with None message
    queue.messages.append(None)
    with pytest.raises(AttributeError):
        processor.process_next()
    
    # Reset and test with non-string message
    queue.messages = [42]
    with pytest.raises(AttributeError):
        processor.process_next()