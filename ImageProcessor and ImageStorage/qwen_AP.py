import pytest
from unittest.mock import MagicMock

class ImageProcessor:
    def __init__(self, storage):
        self.storage = storage

    def process_and_save(self, image_id, original_data):
        # Simulate image processing (convert to grayscale)
        processed_data = f"processed_{original_data}"
        return self.storage.save_image(image_id, processed_data)

    def retrieve_and_enhance(self, image_id):
        data = self.storage.get_image(image_id)
        if data:
            return f"enhanced_{data}"
        return None

class ImageStorage:
    def __init__(self):
        self.images = {}

    def save_image(self, image_id, data):
        self.images[image_id] = data
        return True

    def get_image(self, image_id):
        return self.images.get(image_id)

@pytest.fixture
def image_storage():
    return ImageStorage()

@pytest.fixture
def image_processor(image_storage):
    return ImageProcessor(image_storage)

class TestIntegrationImageProcessorAndImageStorage:

    def test_success_path_process_and_save_image(self, image_processor, image_storage):
        result = image_processor.process_and_save("image1", "original_data")
        assert result == True
        assert image_storage.images["image1"] == "processed_original_data"

    def test_success_path_retrieve_and_enhance_image(self, image_processor, image_storage):
        image_storage.images["image1"] = "processed_original_data"
        result = image_processor.retrieve_and_enhance("image1")
        assert result == "enhanced_processed_original_data"

    def test_partial_failure_save_image_fails(self, image_processor, image_storage):
        image_storage.save_image = MagicMock(return_value=False)
        result = image_processor.process_and_save("image1", "original_data")
        assert result == False
        assert "image1" not in image_storage.images

    def test_partial_failure_retrieve_nonexistent_image(self, image_processor, image_storage):
        result = image_processor.retrieve_and_enhance("image1")
        assert result is None

    def test_edge_case_empty_image_id(self, image_processor, image_storage):
        result = image_processor.process_and_save("", "original_data")
        assert result == True
        assert image_storage.images[""] == "processed_original_data"

    def test_edge_case_empty_image_data(self, image_processor, image_storage):
        result = image_processor.process_and_save("image1", "")
        assert result == True
        assert image_storage.images["image1"] == "processed_"

    def test_edge_case_long_image_id(self, image_processor, image_storage):
        long_image_id = "a" * 100
        result = image_processor.process_and_save(long_image_id, "original_data")
        assert result == True
        assert image_storage.images[long_image_id] == "processed_original_data"

    def test_edge_case_long_image_data(self, image_processor, image_storage):
        long_image_data = "a" * 100
        result = image_processor.process_and_save("image1", long_image_data)
        assert result == True
        assert image_storage.images["image1"] == f"processed_{long_image_data}"

    def test_edge_case_special_characters_in_image_id(self, image_processor, image_storage):
        special_image_id = "image@123#"
        result = image_processor.process_and_save(special_image_id, "original_data")
        assert result == True
        assert image_storage.images[special_image_id] == "processed_original_data"

    def test_edge_case_special_characters_in_image_data(self, image_processor, image_storage):
        special_image_data = "data@123#"
        result = image_processor.process_and_save("image1", special_image_data)
        assert result == True
        assert image_storage.images["image1"] == f"processed_{special_image_data}"