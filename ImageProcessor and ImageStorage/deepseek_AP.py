import pytest
from unittest.mock import MagicMock
from ImageProcessor import ImageProcessor
from ImageStorage import ImageStorage

class TestIntegrationImageProcessor:
    def setup_method(self):
        self.mock_storage = MagicMock(spec=ImageStorage)
        self.processor = ImageProcessor(self.mock_storage)

    def test_process_and_save_success_flow(self):
        self.mock_storage.save_image.return_value = True
        
        result = self.processor.process_and_save("img001", "raw_bytes")
        
        assert result is True
        self.mock_storage.save_image.assert_called_once_with("img001", "processed_raw_bytes")

    def test_retrieve_and_enhance_success_flow(self):
        self.mock_storage.get_image.return_value = "stored_data"
        
        result = self.processor.retrieve_and_enhance("img002")
        
        assert result == "enhanced_stored_data"
        self.mock_storage.get_image.assert_called_once_with("img002")

    def test_storage_save_failure_propagation(self):
        self.mock_storage.save_image.side_effect = IOError("Disk full")
        
        with pytest.raises(IOError) as exc_info:
            self.processor.process_and_save("fail_img", "data")
        assert "Disk full" in str(exc_info.value)

    def test_retrieve_nonexistent_image_handling(self):
        self.mock_storage.get_image.return_value = None
        
        assert self.processor.retrieve_and_enhance("ghost_img") is None
        self.mock_storage.get_image.assert_called_once_with("ghost_img")

    def test_edge_case_empty_data_processing(self):
        self.mock_storage.save_image.return_value = True
        
        result = self.processor.process_and_save("empty_img", "")
        assert result is True
        self.mock_storage.save_image.assert_called_once_with("empty_img", "processed_")

    def test_real_integration_end_to_end(self):
        real_storage = ImageStorage()
        processor = ImageProcessor(real_storage)
        
        processor.process_and_save("real_img", "original_data")
        assert real_storage.images["real_img"] == "processed_original_data"
        assert processor.retrieve_and_enhance("real_img") == "enhanced_processed_original_data"