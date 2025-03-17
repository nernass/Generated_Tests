import pytest
from unittest.mock import Mock, patch, MagicMock
from ImageProcessor import ImageProcessor
from ImageStorage import ImageStorage

class TestImageProcessingIntegration:
    @pytest.fixture
    def mock_storage(self):
        storage = Mock(spec=ImageStorage)
        storage.save_image.return_value = True
        return storage

    @pytest.fixture
    def real_storage(self):
        return ImageStorage()
    
    @pytest.fixture
    def processor_with_mock(self, mock_storage):
        return ImageProcessor(mock_storage)
    
    @pytest.fixture
    def processor_with_real(self, real_storage):
        return ImageProcessor(real_storage)

    # Success path tests
    def test_successful_process_and_save(self, processor_with_mock, mock_storage):
        # Arrange
        image_id = "test123"
        original_data = "raw_image_data"
        
        # Act
        result = processor_with_mock.process_and_save(image_id, original_data)
        
        # Assert
        assert result is True
        mock_storage.save_image.assert_called_once_with(image_id, "processed_raw_image_data")

    def test_successful_end_to_end_flow(self, processor_with_real):
        # Arrange
        image_id = "test456"
        original_data = "original_bytes"
        
        # Act
        save_result = processor_with_real.process_and_save(image_id, original_data)
        retrieve_result = processor_with_real.retrieve_and_enhance(image_id)
        
        # Assert
        assert save_result is True
        assert retrieve_result == "enhanced_processed_original_bytes"

    def test_retrieve_and_enhance_flow(self, processor_with_mock, mock_storage):
        # Arrange
        image_id = "test789"
        mock_storage.get_image.return_value = "stored_processed_data"
        
        # Act
        result = processor_with_mock.retrieve_and_enhance(image_id)
        
        # Assert
        assert result == "enhanced_stored_processed_data"
        mock_storage.get_image.assert_called_once_with(image_id)

    # Failure path tests
    def test_storage_save_failure(self):
        # Arrange
        failing_storage = Mock(spec=ImageStorage)
        failing_storage.save_image.return_value = False
        processor = ImageProcessor(failing_storage)
        
        # Act
        result = processor.process_and_save("fail_id", "data")
        
        # Assert
        assert result is False
        failing_storage.save_image.assert_called_once()

    def test_storage_save_exception(self):
        # Arrange
        failing_storage = Mock(spec=ImageStorage)
        failing_storage.save_image.side_effect = Exception("Storage failure")
        processor = ImageProcessor(failing_storage)
        
        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            processor.process_and_save("fail_id", "data")
        assert "Storage failure" in str(excinfo.value)

    def test_retrieve_non_existent_image(self, processor_with_mock, mock_storage):
        # Arrange
        mock_storage.get_image.return_value = None
        
        # Act
        result = processor_with_mock.retrieve_and_enhance("nonexistent")
        
        # Assert
        assert result is None
        mock_storage.get_image.assert_called_once_with("nonexistent")

    # Edge case tests
    def test_empty_image_data(self, processor_with_real):
        # Arrange
        image_id = "empty_data"
        empty_data = ""
        
        # Act
        save_result = processor_with_real.process_and_save(image_id, empty_data)
        retrieve_result = processor_with_real.retrieve_and_enhance(image_id)
        
        # Assert
        assert save_result is True
        assert retrieve_result == "enhanced_processed_"

    def test_none_image_data(self, processor_with_real):
        # Arrange
        image_id = "none_data"
        none_data = None
        
        # Act
        save_result = processor_with_real.process_and_save(image_id, none_data)
        retrieve_result = processor_with_real.retrieve_and_enhance(image_id)
        
        # Assert
        assert save_result is True
        assert retrieve_result == "enhanced_processed_None"

    def test_large_image_data(self, processor_with_mock, mock_storage):
        # Arrange
        image_id = "large_data"
        large_data = "x" * 1000000  # 1MB of data
        
        # Act
        result = processor_with_mock.process_and_save(image_id, large_data)
        
        # Assert
        assert result is True
        mock_storage.save_image.assert_called_once()
        saved_data = mock_storage.save_image.call_args[0][1]
        assert saved_data.startswith("processed_")
        assert len(saved_data) > 1000000

    def test_multiple_operations_on_same_image(self, processor_with_real):
        # Arrange
        image_id = "multi_op"
        original_data = "original_data"
        
        # Act
        processor_with_real.process_and_save(image_id, original_data)
        first_result = processor_with_real.retrieve_and_enhance(image_id)
        
        # Update the same image
        processor_with_real.process_and_save(image_id, "updated_data")
        second_result = processor_with_real.retrieve_and_enhance(image_id)
        
        # Assert
        assert first_result == "enhanced_processed_original_data"
        assert second_result == "enhanced_processed_updated_data"
        assert first_result != second_result