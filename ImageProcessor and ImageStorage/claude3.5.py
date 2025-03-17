import pytest
from ImageProcessor import ImageProcessor
from ImageStorage import ImageStorage

def test_process_save_and_retrieve():
    # Arrange
    storage = ImageStorage()
    processor = ImageProcessor(storage)
    image_id = "test_image_1"
    original_data = "raw_image_data"

    # Act
    save_result = processor.process_and_save(image_id, original_data)
    enhanced_result = processor.retrieve_and_enhance(image_id)

    # Assert
    assert save_result == True
    assert enhanced_result == "enhanced_processed_raw_image_data"

def test_retrieve_non_existent_image():
    # Arrange
    storage = ImageStorage()
    processor = ImageProcessor(storage)
    
    # Act
    result = processor.retrieve_and_enhance("non_existent")

    # Assert
    assert result is None

def test_multiple_images_processing():
    # Arrange
    storage = ImageStorage()
    processor = ImageProcessor(storage)
    images = {
        "img1": "data1",
        "img2": "data2",
        "img3": "data3"
    }

    # Act & Assert
    for img_id, data in images.items():
        assert processor.process_and_save(img_id, data) == True
        retrieved = processor.retrieve_and_enhance(img_id)
        assert retrieved == f"enhanced_processed_{data}"

def test_storage_processor_independence():
    # Arrange
    storage = ImageStorage()
    processor1 = ImageProcessor(storage)
    processor2 = ImageProcessor(storage)
    image_id = "shared_image"
    
    # Act
    processor1.process_and_save(image_id, "original")
    enhanced1 = processor1.retrieve_and_enhance(image_id)
    enhanced2 = processor2.retrieve_and_enhance(image_id)

    # Assert
    assert enhanced1 == enhanced2
    assert enhanced1 == "enhanced_processed_original"