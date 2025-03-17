class Player:
    def __init__(self, game_world):
        self.inventory = []
        self.location = "forest"
        self.game_world = game_world
        
    def pick_up(self, item):
        location_info = self.game_world.get_location_info(self.location)
        if location_info and item in location_info["items"]:
            self.inventory.append(item)
            self.game_world.remove_item(self.location, item)
            return True
        return False