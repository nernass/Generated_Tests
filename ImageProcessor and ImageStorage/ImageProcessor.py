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