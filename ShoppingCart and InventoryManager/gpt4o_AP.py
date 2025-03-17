import pytest
from unittest.mock import patch, MagicMock
from InventoryManager import InventoryManager
from ShoppingCart import ShoppingCart

class TestShoppingCartInventoryIntegration:
    @pytest.fixture
    def inventory_manager(self):
        manager = InventoryManager()
        # Setup test data
        manager.add_product("item1", 10.0, 5)  # id, price, stock
        manager.add_product("item2", 20.0, 3)
        manager.add_product("item3", 15.0, 0)  # Out of stock item
        manager.add_product("item4", 5.0, 100)  # High stock item
        manager.add_product("free_item", 0.0, 10)  # Free item
        return manager

    @pytest.fixture
    def shopping_cart(self, inventory_manager):
        return ShoppingCart(inventory_manager)

    def test_successful_purchase_flow(self, shopping_cart):
        # Test adding available items and calculating total
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.add_item("item2", 1) == True
        assert shopping_cart.get_total() == 40.0  # (2 * 10.0) + (1 * 20.0)
        # Verify cart contents
        assert shopping_cart.items == {"item1": 2, "item2": 1}

    def test_out_of_stock_handling(self, shopping_cart):
        # Test adding item with insufficient stock
        assert shopping_cart.add_item("item1", 6) == False  # Only 5 in stock
        assert shopping_cart.add_item("item3", 1) == False  # 0 in stock
        assert shopping_cart.get_total() == 0.0
        # Verify cart remains empty
        assert not shopping_cart.items

    def test_invalid_item_handling(self, shopping_cart):
        # Test adding non-existent item
        assert shopping_cart.add_item("nonexistent", 1) == False
        assert shopping_cart.get_total() == 0.0
        assert not shopping_cart.items

    def test_multiple_add_same_item(self, shopping_cart):
        # Test adding same item multiple times
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.get_total() == 40.0  # 4 * 10.0
        assert shopping_cart.items == {"item1": 4}

    def test_mixed_valid_invalid_items(self, shopping_cart):
        # Test mixing valid and invalid operations
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.add_item("nonexistent", 1) == False
        assert shopping_cart.add_item("item3", 1) == False  # Out of stock
        assert shopping_cart.add_item("item2", 1) == True
        assert shopping_cart.get_total() == 40.0  # (2 * 10.0) + (1 * 20.0)
        assert shopping_cart.items == {"item1": 2, "item2": 1}

    def test_edge_case_zero_quantity(self, shopping_cart):
        # Test adding zero quantity
        assert shopping_cart.add_item("item1", 0) == True
        assert shopping_cart.get_total() == 0.0
        assert shopping_cart.items == {"item1": 0}

    def test_free_items(self, shopping_cart):
        # Test adding items with zero price
        assert shopping_cart.add_item("free_item", 5) == True
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.get_total() == 20.0  # (5 * 0.0) + (2 * 10.0)
        assert shopping_cart.items == {"free_item": 5, "item1": 2}

    def test_inventory_integration_with_mocked_check_availability(self, inventory_manager):
        # Test with mocked inventory behavior
        with patch.object(inventory_manager, 'check_availability', return_value=False) as mock_check:
            cart = ShoppingCart(inventory_manager)
            result = cart.add_item("item4", 5)
            assert result == False
            mock_check.assert_called_once_with("item4", 5)
            assert not cart.items

    def test_inventory_integration_with_mocked_get_price(self, inventory_manager):
        # Test with mocked price behavior
        with patch.object(inventory_manager, 'get_price', return_value=50.0) as mock_price:
            cart = ShoppingCart(inventory_manager)
            # First ensure item is available
            with patch.object(inventory_manager, 'check_availability', return_value=True):
                cart.add_item("item1", 2)
            # Now test price calculation with mocked price
            total = cart.get_total()
            assert total == 100.0  # 2 * 50.0 (mocked price)
            mock_price.assert_called_with("item1")

    def test_large_quantity_handling(self, inventory_manager):
        # Test with a very large quantity
        inventory_manager.add_product("bulk_item", 0.01, 10000)
        cart = ShoppingCart(inventory_manager)
        assert cart.add_item("bulk_item", 9999) == True
        assert cart.add_item("bulk_item", 2) == False  # Would exceed stock
        assert cart.get_total() == 99.99  # 9999 * 0.01

    def test_negative_quantity_handling(self, shopping_cart):
        # Test with negative quantity
        assert shopping_cart.add_item("item1", -1) == False
        assert not shopping_cart.items
        
    def test_exception_handling(self, inventory_manager):
        # Test handling exceptions from inventory manager
        cart = ShoppingCart(inventory_manager)
        
        # Mock check_availability to raise an exception
        with patch.object(inventory_manager, 'check_availability', 
                          side_effect=Exception("Inventory system error")):
            try:
                result = cart.add_item("item1", 1)
                # If no exception propagation, cart should be in consistent state
                assert not cart.items
            except Exception:
                # If exception propagates, this will be caught here
                pass