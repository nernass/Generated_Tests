import pytest
from unittest.mock import Mock, patch
from Player import Player
from GameWorld import GameWorld

@pytest.fixture
def game_world():
    return GameWorld()

@pytest.fixture
def player(game_world):
    return Player(game_world)

def test_player_picks_up_existing_item(player, game_world):
    # Mock get_location_info to return a specific location info
    with patch.object(game_world, 'get_location_info', return_value={"items": ["mushroom", "stick"]}):
        result = player.pick_up("mushroom")
        assert result == True
        assert "mushroom" in player.inventory
        assert "mushroom" not in game_world.locations["forest"]["items"]

def test_player_cannot_pick_up_nonexistent_item(player, game_world):
    with patch.object(game_world, 'get_location_info', return_value={"items": ["mushroom", "stick"]}):
        result = player.pick_up("invalid_item")
        assert result == False
        assert "invalid_item" not in player.inventory

def test_player_picks_up_multiple_items(player, game_world):
    with patch.object(game_world, 'get_location_info', return_value={"items": ["mushroom", "stick"]}):
        player.pick_up("mushroom")
        player.pick_up("stick")
        assert "mushroom" in player.inventory
        assert "stick" in player.inventory
        assert "mushroom" not in game_world.locations["forest"]["items"]
        assert "stick" not in game_world.locations["forest"]["items"]

def test_player_picks_up_from_different_locations(player, game_world):
    with patch.object(game_world, 'get_location_info', side_effect=[
        {"items": ["mushroom", "stick"]},
        {"items": ["gem", "rock"]}
    ]):
        player.pick_up("mushroom")
        player.location = "cave"
        player.pick_up("gem")
        assert "mushroom" in player.inventory
        assert "gem" in player.inventory
        assert "mushroom" not in game_world.locations["forest"]["items"]
        assert "gem" not in game_world.locations["cave"]["items"]

def test_invalid_location(player, game_world):
    with patch.object(game_world, 'get_location_info', return_value=None):
        player.location = "mountain"
        result = player.pick_up("anything")
        assert result == False
        assert "anything" not in player.inventory

def test_remove_item_directly(game_world):
    result = game_world.remove_item("forest", "mushroom")
    assert result == True
    assert "mushroom" not in game_world.locations["forest"]["items"]

def test_remove_nonexistent_item(game_world):
    result = game_world.remove_item("forest", "apple")
    assert result == False
    assert "apple" not in game_world.locations["forest"]["items"]

def test_remove_from_nonexistent_location(game_world):
    result = game_world.remove_item("mountain", "rock")
    assert result == False