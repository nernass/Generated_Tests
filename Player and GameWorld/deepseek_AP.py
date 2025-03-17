import pytest
from unittest.mock import MagicMock
from GameWorld import GameWorld
from Player import Player

class TestIntegrationGamePlayer:
    def setup_method(self):
        self.mock_world = MagicMock(spec=GameWorld)
        self.player = Player(self.mock_world)

    def test_valid_item_pickup_flow(self):
        self.mock_world.get_location_info.return_value = {
            "items": ["mushroom", "stick"]
        }
        self.mock_world.remove_item.return_value = True
        
        assert self.player.pick_up("mushroom") is True
        assert "mushroom" in self.player.inventory
        self.mock_world.get_location_info.assert_called_once_with("forest")
        self.mock_world.remove_item.assert_called_once_with("forest", "mushroom")

    def test_gameworld_remove_failure_propagation(self):
        self.mock_world.get_location_info.return_value = {"items": ["gem"]}
        self.mock_world.remove_item.side_effect = RuntimeError("Item removal failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            self.player.pick_up("gem")
        assert "Item removal failed" in str(exc_info.value)

    def test_nonexistent_item_handling(self):
        self.mock_world.get_location_info.return_value = {"items": ["stick"]}
        
        assert self.player.pick_up("gem") is False
        assert len(self.player.inventory) == 0
        self.mock_world.remove_item.assert_not_called()

    def test_invalid_location_edge_case(self):
        self.mock_world.get_location_info.return_value = None
        
        assert self.player.pick_up("rock") is False
        self.mock_world.remove_item.assert_not_called()

    def test_empty_items_edge_case(self):
        self.mock_world.get_location_info.return_value = {"items": []}
        
        assert self.player.pick_up("stick") is False
        self.mock_world.remove_item.assert_not_called()

    def test_real_integration_end_to_end(self):
        real_world = GameWorld()
        player = Player(real_world)
        
        assert player.pick_up("mushroom") is True
        assert "mushroom" in player.inventory
        assert "mushroom" not in real_world.locations["forest"]["items"]
        assert real_world.get_location_info("forest")["items"] == ["stick"]