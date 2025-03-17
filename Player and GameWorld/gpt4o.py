import pytest
from Player import Player
from GameWorld import GameWorld

def test_player_picks_up_existing_item():
    game_world = GameWorld()
    player = Player(game_world)
    
    # Initial state checks
    assert "mushroom" in game_world.locations["forest"]["items"]
    assert len(player.inventory) == 0
    
    # Perform pickup
    result = player.pick_up("mushroom")
    
    # Verify results
    assert result == True
    assert "mushroom" in player.inventory
    assert "mushroom" not in game_world.locations["forest"]["items"]

def test_player_cannot_pick_up_nonexistent_item():
    game_world = GameWorld()
    player = Player(game_world)
    
    # Try to pick up item that doesn't exist
    result = player.pick_up("invalid_item")
    
    # Verify results
    assert result == False
    assert len(player.inventory) == 0
    assert len(game_world.locations["forest"]["items"]) == 2

def test_player_picks_up_multiple_items():
    game_world = GameWorld()
    player = Player(game_world)
    
    # Pick up both items from forest
    player.pick_up("mushroom")
    player.pick_up("stick")
    
    # Verify results
    assert len(player.inventory) == 2
    assert "mushroom" in player.inventory
    assert "stick" in player.inventory
    assert len(game_world.locations["forest"]["items"]) == 0

def test_player_picks_up_from_different_locations():
    game_world = GameWorld()
    player = Player(game_world)
    
    # Pick up from forest
    player.pick_up("mushroom")
    
    # Move to cave and pick up
    player.location = "cave"
    player.pick_up("gem")
    
    # Verify results
    assert len(player.inventory) == 2
    assert "mushroom" in player.inventory
    assert "gem" in player.inventory
    assert "mushroom" not in game_world.locations["forest"]["items"]
    assert "gem" not in game_world.locations["cave"]["items"]

def test_invalid_location():
    game_world = GameWorld()
    player = Player(game_world)
    
    # Set invalid location
    player.location = "mountain"
    
    # Try to pick up
    result = player.pick_up("anything")
    
    # Verify results
    assert result == False
    assert len(player.inventory) == 0

def test_remove_item_directly():
    game_world = GameWorld()
    
    # Remove item directly
    result = game_world.remove_item("forest", "mushroom")
    
    # Verify results
    assert result == True
    assert "mushroom" not in game_world.locations["forest"]["items"]
    assert len(game_world.locations["forest"]["items"]) == 1

def test_remove_nonexistent_item():
    game_world = GameWorld()
    
    # Try to remove item that doesn't exist
    result = game_world.remove_item("forest", "apple")
    
    # Verify results
    assert result == False
    assert len(game_world.locations["forest"]["items"]) == 2

def test_remove_from_nonexistent_location():
    game_world = GameWorld()
    
    # Try to remove from location that doesn't exist
    result = game_world.remove_item("mountain", "rock")
    
    # Verify results
    assert result == False