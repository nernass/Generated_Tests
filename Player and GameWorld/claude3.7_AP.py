import pytest
from unittest.mock import Mock, patch, call
import logging
from Player import Player
from GameWorld import GameWorld

# Setup logging for testing error handling
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def game_world():
    return GameWorld()

@pytest.fixture
def player(game_world):
    return Player(game_world)

@pytest.fixture
def mock_game_world():
    return Mock(spec=GameWorld)

@pytest.fixture
def player_with_mock(mock_game_world):
    return Player(mock_game_world)

# Success Path Tests
def test_success_path_pick_up_item(player, game_world):
    """Test the complete flow: Player picks up item, item is added to inventory and removed from location"""
    # Initial state verification
    assert "mushroom" in game_world.locations["forest"]["items"]
    assert len(player.inventory) == 0
    
    # Execute workflow
    result = player.pick_up("mushroom")
    
    # Assert results
    assert result is True
    assert "mushroom" in player.inventory
    assert "mushroom" not in game_world.locations["forest"]["items"]

def test_success_path_pick_up_multiple_items(player, game_world):
    """Test picking up multiple items works correctly"""
    # Execute workflow
    player.pick_up("mushroom")
    player.pick_up("stick")
    
    # Assert results
    assert len(player.inventory) == 2
    assert "mushroom" in player.inventory
    assert "stick" in player.inventory
    assert len(game_world.locations["forest"]["items"]) == 0

def test_success_path_location_change(player, game_world):
    """Test player can change location and pick up items from different locations"""
    player.pick_up("mushroom")
    player.location = "cave"
    player.pick_up("gem")
    
    assert len(player.inventory) == 2
    assert "mushroom" in player.inventory
    assert "gem" in player.inventory
    assert "gem" not in game_world.locations["cave"]["items"]

# Failure Path Tests
def test_failure_get_location_info_returns_none(player_with_mock, mock_game_world):
    """Test behavior when get_location_info fails by returning None"""
    # Setup mock to simulate failure
    mock_game_world.get_location_info.return_value = None
    
    # Execute workflow
    result = player_with_mock.pick_up("mushroom")
    
    # Assert results
    assert result is False
    assert len(player_with_mock.inventory) == 0
    mock_game_world.get_location_info.assert_called_once_with("forest")
    mock_game_world.remove_item.assert_not_called()

def test_failure_get_location_info_raises_exception(player_with_mock, mock_game_world):
    """Test behavior when get_location_info raises an exception"""
    # Setup mock to raise exception
    mock_game_world.get_location_info.side_effect = Exception("Database connection error")
    
    # Execute workflow and expect exception to propagate
    with pytest.raises(Exception) as exc_info:
        player_with_mock.pick_up("mushroom")
    
    assert "Database connection error" in str(exc_info.value)
    assert len(player_with_mock.inventory) == 0
    mock_game_world.remove_item.assert_not_called()

def test_failure_remove_item_returns_false(player_with_mock, mock_game_world):
    """Test behavior when remove_item fails by returning False"""
    # Setup mock
    mock_game_world.get_location_info.return_value = {"items": ["mushroom"]}
    mock_game_world.remove_item.return_value = False
    
    # Execute workflow
    result = player_with_mock.pick_up("mushroom")
    
    # Despite remove_item failing, the item is added to inventory
    # This highlights a potential issue in the implementation
    assert result is True
    assert "mushroom" in player_with_mock.inventory
    mock_game_world.remove_item.assert_called_once_with("forest", "mushroom")

def test_failure_remove_item_raises_exception(player_with_mock, mock_game_world):
    """Test behavior when remove_item raises an exception"""
    # Setup mock
    mock_game_world.get_location_info.return_value = {"items": ["mushroom"]}
    mock_game_world.remove_item.side_effect = Exception("Failed to update database")
    
    # Execute workflow and expect exception to propagate
    with pytest.raises(Exception) as exc_info:
        player_with_mock.pick_up("mushroom")
    
    assert "Failed to update database" in str(exc_info.value)
    # Item was added to inventory before exception was raised
    # This highlights another potential issue with transaction handling
    assert "mushroom" in player_with_mock.inventory

# Edge Case Tests
def test_edge_case_empty_location(player, game_world):
    """Test picking up from an empty location"""
    # Make location empty
    game_world.locations["forest"]["items"] = []
    
    result = player.pick_up("mushroom")
    assert result is False
    assert len(player.inventory) == 0

def test_edge_case_invalid_location(player, game_world):
    """Test picking up from a non-existent location"""
    player.location = "mountain"
    result = player.pick_up("gold")
    
    assert result is False
    assert len(player.inventory) == 0

def test_edge_case_duplicate_items(player, game_world):
    """Test picking up duplicated items"""
    # Add duplicate item
    game_world.locations["forest"]["items"].append("mushroom")
    
    # Pick up first mushroom
    player.pick_up("mushroom")
    assert "mushroom" in player.inventory
    assert "mushroom" in game_world.locations["forest"]["items"]
    
    # Pick up second mushroom
    player.pick_up("mushroom")
    assert player.inventory.count("mushroom") == 2
    assert "mushroom" not in game_world.locations["forest"]["items"]

def test_data_flow_between_components(player_with_mock, mock_game_world):
    """Test the data flow between components"""
    # Setup mock
    mock_game_world.get_location_info.return_value = {"items": ["crystal"]}
    mock_game_world.remove_item.return_value = True
    
    # Execute workflow
    result = player_with_mock.pick_up("crystal")
    
    # Assert data flow
    assert result is True
    assert "crystal" in player_with_mock.inventory
    mock_game_world.get_location_info.assert_called_once_with("forest")
    mock_game_world.remove_item.assert_called_once_with("forest", "crystal")

def test_integration_with_real_components():
    """Integration test with real components"""
    game_world = GameWorld()
    player = Player(game_world)
    
    # Test initial state
    assert "mushroom" in game_world.locations["forest"]["items"]
    assert "stick" in game_world.locations["forest"]["items"]
    assert len(player.inventory) == 0
    
    # Pick up item
    player.pick_up("mushroom")
    
    # Verify state changes
    assert "mushroom" in player.inventory
    assert "mushroom" not in game_world.locations["forest"]["items"]
    assert "stick" in game_world.locations["forest"]["items"]
    
    # Change location and pick up another item
    player.location = "cave"
    player.pick_up("gem")
    
    # Verify updated state
    assert len(player.inventory) == 2
    assert "gem" in player.inventory
    assert "gem" not in game_world.locations["cave"]["items"]
    assert "rock" in game_world.locations["cave"]["items"]