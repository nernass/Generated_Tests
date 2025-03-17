import pytest
from unittest.mock import Mock, patch
from ImageProcessor import ImageProcessor
from ImageStorage import ImageStorage

@pytest.fixture
def mock_storage():
    return Mock(spec=ImageStorage)

@pytest.fixture
def processor(mock_storage):
    return ImageProcessor(mock_storage)

def test_process_save_and_retrieve(processor, mock_storage):
    # Arrange
    image_id = "test_image_1"
    original_data = "raw_image_data"
    mock_storage.save_image.return_value = True
    mock_storage.get_image.return_value = f"processed_{original_data}"

    # Act
    save_result = processor.process_and_save(image_id, original_data)
    retrieved_data = processor.retrieve_and_enhance(image_id)

    # Assert
    assert save_result == True
    assert retrieved_data == "enhanced_processed_raw_image_data"
    mock_storage.save_image.assert_called_once_with(image_id, f"processed_{original_data}")
    mock_storage.get_image.assert_called_once_with(image_id)

def test_retrieve_non_existent_image(processor, mock_storage):
    # Arrange
    mock_storage.get_image.return_value = None

    # Act
    result = processor.retrieve_and_enhance("non_existent")

    # Assert
    assert result is None
    mock_storage.get_image.assert_called_once_with("non_existent")

def test_multiple_images_processing(processor, mock_storage):
    # Arrange
    images = {
        "img1": "data1",
        "img2": "data2",
        "img3": "data3"
    }
    mock_storage.save_image.return_value = True

    # Act & Assert
    for img_id, data in images.items():
        mock_storage.get_image.return_value = f"processed_{data}"
        assert processor.process_and_save(img_id, data) == True
        assert processor.retrieve_and_enhance(img_id) == f"enhanced_processed_{data}"
        mock_storage.save_image.assert_any_call(img_id, f"processed_{data}")
        mock_storage.get_image.assert_any_call(img_id)

def test_storage_direct_access(processor, mock_storage):
    # Arrange
    image_id = "direct_access_test"
    original_data = "original_bytes"
    mock_storage.save_image.return_value = True
    mock_storage.get_image.return_value = f"processed_{original_data}"

    # Act
    processor.process_and_save(image_id, original_data)
    raw_stored_data = mock_storage.get_image(image_id)
    enhanced_data = processor.retrieve_and_enhance(image_id)

    # Assert
    assert raw_stored_data == f"processed_{original_data}"
    assert enhanced_data == f"enhanced_processed_{original_data}"
    mock_storage.save_image.assert_called_once_with(image_id, f"processed_{original_data}")
    mock_storage.get_image.assert_called_with(image_id)

def test_shared_storage():
    # Arrange
    shared_storage = ImageStorage()
    processor1 = ImageProcessor(shared_storage)
    processor2 = ImageProcessor(shared_storage)
    image_id = "shared_image"
    
    # Act
    processor1.process_and_save(image_id, "original")
    result1 = processor1.retrieve_and_enhance(image_id)
    result2 = processor2.retrieve_and_enhance(image_id)

    # Assert
    assert result1 == result2
    assert result1 == "enhanced_processed_original"