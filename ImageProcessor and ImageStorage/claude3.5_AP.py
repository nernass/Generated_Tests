import pytest
from unittest.mock import Mock, patch
import logging
from ImageProcessor import ImageProcessor
from ImageStorage import ImageStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestImageIntegration:
    @pytest.fixture
    def mock_storage(self):
        mock = Mock(spec=ImageStorage)
        mock.save_image.return_value = True
        return mock

    @pytest.fixture
    def processor(self, mock_storage):
        return ImageProcessor(mock_storage)

    # Success Path Tests
    def test_successful_workflow(self, processor, mock_storage):
        # Arrange
        image_id = "test_image"
        input_data = "raw_data"
        mock_storage.get_image.return_value = "processed_raw_data"

        # Act
        save_result = processor.process_and_save(image_id, input_data)
        retrieve_result = processor.retrieve_and_enhance(image_id)

        # Assert
        assert save_result is True
        assert retrieve_result == "enhanced_processed_raw_data"
        mock_storage.save_image.assert_called_once_with(image_id, "processed_raw_data")
        mock_storage.get_image.assert_called_once_with(image_id)

    # Failure Path Tests
    def test_storage_save_failure(self, processor, mock_storage):
        # Arrange
        mock_storage.save_image.return_value = False
        
        # Act
        result = processor.process_and_save("fail_id", "data")

        # Assert
        assert result is False
        mock_storage.save_image.assert_called_once()

    def test_storage_exception_handling(self, processor, mock_storage):
        # Arrange
        mock_storage.save_image.side_effect = Exception("Storage error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            processor.process_and_save("error_id", "data")
        assert "Storage error" in str(exc_info.value)

    # Edge Cases Tests
    def test_empty_input(self, processor, mock_storage):
        # Arrange
        image_id = "empty_test"
        
        # Act
        processor.process_and_save(image_id, "")
        mock_storage.get_image.return_value = "processed_"
        result = processor.retrieve_and_enhance(image_id)

        # Assert
        assert result == "enhanced_processed_"
        mock_storage.save_image.assert_called_once_with(image_id, "processed_")

    def test_none_input(self, processor, mock_storage):
        # Arrange
        image_id = "none_test"
        
        # Act
        processor.process_and_save(image_id, None)
        mock_storage.get_image.return_value = "processed_None"
        result = processor.retrieve_and_enhance(image_id)

        # Assert
        assert result == "enhanced_processed_None"
        mock_storage.save_image.assert_called_once_with(image_id, "processed_None")

    def test_large_input(self, processor, mock_storage):
        # Arrange
        image_id = "large_test"
        large_data = "x" * 1000000  # 1MB of data
        
        # Act
        result = processor.process_and_save(image_id, large_data)

        # Assert
        assert result is True
        mock_storage.save_image.assert_called_once()
        saved_data = mock_storage.save_image.call_args[0][1]
        assert len(saved_data) > 1000000

    # Data Flow Tests
    def test_data_transformation_flow(self, processor, mock_storage):
        # Arrange
        image_id = "flow_test"
        original_data = "original"
        processed_data = "processed_original"
        enhanced_data = "enhanced_processed_original"

        # Act
        mock_storage.get_image.return_value = processed_data
        save_result = processor.process_and_save(image_id, original_data)
        enhanced_result = processor.retrieve_and_enhance(image_id)

        # Assert
        assert save_result is True
        assert enhanced_result == enhanced_data
        mock_storage.save_image.assert_called_once_with(image_id, processed_data)
        mock_storage.get_image.assert_called_once_with(image_id)

    def test_multiple_operations(self, processor, mock_storage):
        # Arrange
        operations = [
            ("img1", "data1"),
            ("img2", "data2"),
            ("img3", "data3")
        ]

        # Act & Assert
        for img_id, data in operations:
            mock_storage.get_image.return_value = f"processed_{data}"
            save_result = processor.process_and_save(img_id, data)
            retrieve_result = processor.retrieve_and_enhance(img_id)
            
            assert save_result is True
            assert retrieve_result == f"enhanced_processed_{data}"
            mock_storage.save_image.assert_any_call(img_id, f"processed_{data}")