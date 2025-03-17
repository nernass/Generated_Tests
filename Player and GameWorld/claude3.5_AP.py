import pytest
from unittest.mock import Mock, patch
import logging
from Player import Player
from GameWorld import GameWorld

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestGameIntegration:
    @pytest.fixture
    def mock_game_world(self):
        return Mock(spec=GameWorld)

    @pytest.fixture
    def real_game_world(self):
        return GameWorld()

    @pytest.fixture
    def player_with_mock(self, mock_game_world):
        return Player(mock_game_world)

    @pytest.fixture
    def player_with_real(self, real_game_world):
        return Player(real_game_world)

    # Success Path Tests
    def test_successful_item_pickup(self, player_with_real, real_game_world):
        """Test successful end-to-end item pickup flow"""
        initial_forest_items = len(real_game_world.locations["forest"]["items"])
        result = player_with_real.pick_up("mushroom")
        
        assert result is True
        assert "mushroom" in player_with_real.inventory
        assert len(real_game_world.locations["forest"]["items"]) == initial_forest_items - 1
        assert "mushroom" not in real_game_world.locations["forest"]["items"]

    # Failure Path Tests
    def test_failed_location_info_retrieval(self, player_with_mock, mock_game_world):
        """Test system behavior when location info retrieval fails"""
        mock_game_world.get_location_info.return_value = None
        
        result = player_with_mock.pick_up("mushroom")
        
        assert result is False
        assert len(player_with_mock.inventory) == 0
        mock_game_world.get_location_info.assert_called_once_with("forest")
        mock_game_world.remove_item.assert_not_called()

    def test_failed_item_removal(self, player_with_mock, mock_game_world):
        """Test system behavior when item removal fails"""
        mock_game_world.get_location_info.return_value = {"items": ["mushroom"]}
        mock_game_world.remove_item.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            player_with_mock.pick_up("mushroom")
        
        assert "Database error" in str(exc_info.value)
        mock_game_world.remove_item.assert_called_once_with("forest", "mushroom")

    # Edge Cases
    def test_empty_location(self, player_with_mock, mock_game_world):
        """Test pickup from empty location"""
        mock_game_world.get_location_info.return_value = {"items": []}
        
        result = player_with_mock.pick_up("mushroom")
        
        assert result is False
        assert len(player_with_mock.inventory) == 0

    def test_nonexistent_location(self, player_with_mock, mock_game_world):
        """Test pickup from nonexistent location"""
        player_with_mock.location = "void"
        mock_game_world.get_location_info.return_value = None
        
        result = player_with_mock.pick_up("mushroom")
        
        assert result is False
        assert len(player_with_mock.inventory) == 0

    # Data Flow Tests
    def test_component_interaction_flow(self, player_with_mock, mock_game_world):
        """Test the data flow between components"""
        mock_game_world.get_location_info.return_value = {"items": ["mushroom"]}
        mock_game_world.remove_item.return_value = True
        
        result = player_with_mock.pick_up("mushroom")
        
        assert result is True
        mock_game_world.get_location_info.assert_called_once_with("forest")
        mock_game_world.remove_item.assert_called_once_with("forest", "mushroom")
        assert "mushroom" in player_with_mock.inventory

    # Full Integration Test
    def test_complete_gameplay_flow(self, player_with_real, real_game_world):
        """Test complete gameplay flow with real components"""
        # Initial state verification
        assert "mushroom" in real_game_world.locations["forest"]["items"]
        assert len(player_with_real.inventory) == 0
        
        # Pick up from forest
        player_with_real.pick_up("mushroom")
        assert "mushroom" in player_with_real.inventory
        assert "mushroom" not in real_game_world.locations["forest"]["items"]
        
        # Change location and pick up from cave
        player_with_real.location = "cave"
        player_with_real.pick_up("gem")
        
        assert len(player_with_real.inventory) == 2
        assert "gem" in player_with_real.inventory
        assert "gem" not in real_game_world.locations["cave"]["items"]