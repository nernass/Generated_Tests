import pytest

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

@pytest.fixture
def game_world():
    return GameWorld()

@pytest.fixture
def player(game_world):
    return Player(game_world)

class TestIntegrationGameWorldAndPlayer:

    def test_success_path_pick_up_item_from_forest(self, player, game_world):
        result = player.pick_up("mushroom")
        assert result == True
        assert player.inventory == ["mushroom"]
        assert game_world.locations["forest"]["items"] == ["stick"]

    def test_success_path_pick_up_item_from_cave(self, player, game_world):
        player.location = "cave"
        result = player.pick_up("gem")
        assert result == True
        assert player.inventory == ["gem"]
        assert game_world.locations["cave"]["items"] == ["rock"]

    def test_partial_failure_item_not_in_location(self, player, game_world):
        result = player.pick_up("rock")
        assert result == False
        assert player.inventory == []
        assert game_world.locations["forest"]["items"] == ["mushroom", "stick"]

    def test_partial_failure_location_does_not_exist(self, player, game_world):
        player.location = "desert"
        result = player.pick_up("mushroom")
        assert result == False
        assert player.inventory == []
        assert game_world.locations["forest"]["items"] == ["mushroom", "stick"]

    def test_edge_case_pick_up_same_item_twice(self, player, game_world):
        player.pick_up("mushroom")
        result = player.pick_up("mushroom")
        assert result == False
        assert player.inventory == ["mushroom"]
        assert game_world.locations["forest"]["items"] == ["stick"]

    def test_edge_case_empty_item_name(self, player, game_world):
        result = player.pick_up("")
        assert result == False
        assert player.inventory == []
        assert game_world.locations["forest"]["items"] == ["mushroom", "stick"]

    def test_edge_case_special_characters_in_item_name(self, player, game_world):
        result = player.pick_up("!@#")
        assert result == False
        assert player.inventory == []
        assert game_world.locations["forest"]["items"] == ["mushroom", "stick"]

    def test_edge_case_large_item_name(self, player, game_world):
        long_item_name = "a" * 100
        result = player.pick_up(long_item_name)
        assert result == False
        assert player.inventory == []
        assert game_world.locations["forest"]["items"] == ["mushroom", "stick"]

    def test_edge_case_change_location_and_pick_up_item(self, player, game_world):
        player.location = "cave"
        result = player.pick_up("rock")
        assert result == True
        assert player.inventory == ["rock"]
        assert game_world.locations["cave"]["items"] == ["gem"]