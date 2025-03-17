import pytest
from InventoryManager import InventoryManager
from ShoppingCart import ShoppingCart

class TestIntegration:
    @pytest.fixture
    def inventory_manager(self):
        inventory = InventoryManager()
        # Add test products
        inventory.add_product("item1", 10.0, 5)  # id, price, stock
        inventory.add_product("item2", 15.0, 3)
        inventory.add_product("item3", 5.0, 0)  # Out of stock item
        return inventory
    
    @pytest.fixture
    def shopping_cart(self, inventory_manager):
        return ShoppingCart(inventory_manager)
    
    def test_add_available_item(self, shopping_cart):
        # Test adding an available item
        result = shopping_cart.add_item("item1", 2)
        assert result == True
        assert shopping_cart.items["item1"] == 2
    
    def test_add_unavailable_item(self, shopping_cart):
        # Test adding an item with insufficient stock
        result = shopping_cart.add_item("item3", 1)
        assert result == False
        assert "item3" not in shopping_cart.items
    
    def test_add_nonexistent_item(self, shopping_cart):
        # Test adding an item that doesn't exist in inventory
        result = shopping_cart.add_item("item4", 1)
        assert result == False
        assert "item4" not in shopping_cart.items
    
    def test_add_beyond_availability(self, shopping_cart):
        # Test adding more quantity than available
        result = shopping_cart.add_item("item2", 4)
        assert result == False
        assert "item2" not in shopping_cart.items
    
    def test_add_multiple_items(self, shopping_cart):
        # Test adding multiple different items
        shopping_cart.add_item("item1", 1)
        shopping_cart.add_item("item2", 2)
        assert len(shopping_cart.items) == 2
        assert shopping_cart.items["item1"] == 1
        assert shopping_cart.items["item2"] == 2
    
    def test_add_same_item_multiple_times(self, shopping_cart):
        # Test adding the same item multiple times
        shopping_cart.add_item("item1", 1)
        shopping_cart.add_item("item1", 2)
        assert shopping_cart.items["item1"] == 3
    
    def test_get_total(self, shopping_cart):
        # Test calculating the total price
        shopping_cart.add_item("item1", 2)  # 2 × $10.0 = $20.0
        shopping_cart.add_item("item2", 1)  # 1 × $15.0 = $15.0
        expected_total = 35.0
        assert shopping_cart.get_total() == expected_total
    
    def test_inventory_price_change_reflection(self, inventory_manager, shopping_cart):
        # Test that price changes in inventory are reflected in the cart total
        shopping_cart.add_item("item1", 1)
        original_total = shopping_cart.get_total()
        
        # Update price in inventory
        inventory_manager.inventory["item1"]["price"] = 20.0
        
        # Total should now reflect the new price
        assert shopping_cart.get_total() == 20.0
        assert shopping_cart.get_total() != original_total