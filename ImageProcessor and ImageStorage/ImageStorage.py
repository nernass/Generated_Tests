class ImageStorage:
    def __init__(self):
        self.images = {}
        
    def save_image(self, image_id, data):
        self.images[image_id] = data
        return True
        
    def get_image(self, image_id):
        return self.images.get(image_id)

