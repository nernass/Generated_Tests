class GameWorld:
    def __init__(self):
        self.locations = {
            "forest": {"description": "A dense forest", "items": ["mushroom", "stick"]},
            "cave": {"description": "A dark cave", "items": ["gem", "rock"]}
        }
        
    def get_location_info(self, location):
        if location in self.locations:
            return self.locations[location]
        return None
        
    def remove_item(self, location, item):
        if location in self.locations and item in self.locations[location]["items"]:
            self.locations[location]["items"].remove(item)
            return True
        return False
        
