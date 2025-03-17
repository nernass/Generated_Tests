import pytest
from unittest.mock import MagicMock
from ImageProcessor import ImageProcessor
from ImageStorage import ImageStorage

class TestIntegrationImageProcessor:
    def setup_method(self):
        self.mock_storage = MagicMock(spec=ImageStorage)
        self.processor = ImageProcessor(self.mock_storage)

    def test_process_and_save_success(self):
        self.mock_storage.save_image.return_value = True
        
        result = self.processor.process_and_save("img123", "raw_data")
        
        assert result is True
        self.mock_storage.save_image.assert_called_once_with("img123", "processed_raw_data")

    def test_retrieve_and_enhance_success(self):
        self.mock_storage.get_image.return_value = "stored_data"
        
        result = self.processor.retrieve_and_enhance("img456")
        
        assert result == "enhanced_stored_data"
        self.mock_storage.get_image.assert_called_once_with("img456")

    def test_storage_failure_propagation(self):
        self.mock_storage.save_image.side_effect = Exception("Storage error")
        
        with pytest.raises(Exception) as exc_info:
            self.processor.process_and_save("fail_id", "data")
        assert "Storage error" in str(exc_info.value)

    def test_retrieve_nonexistent_image(self):
        self.mock_storage.get_image.return_value = None
        
        assert self.processor.retrieve_and_enhance("ghost_id") is None
        self.mock_storage.get_image.assert_called_once_with("ghost_id")

    def test_edge_case_empty_image_data(self):
        self.mock_storage.save_image.return_value = True
        
        result = self.processor.process_and_save("empty_img", "")
        assert result is True
        self.mock_storage.save_image.assert_called_once_with("empty_img", "processed_")

    def test_real_integration_flow(self):
        real_storage = ImageStorage()
        processor = ImageProcessor(real_storage)
        
        processor.process_and_save("real_img", "original")
        assert real_storage.images["real_img"] == "processed_original"
        assert processor.retrieve_and_enhance("real_img") == "enhanced_processed_original"