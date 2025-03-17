import pytest
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
        return manager

    @pytest.fixture
    def shopping_cart(self, inventory_manager):
        return ShoppingCart(inventory_manager)

    def test_successful_purchase_flow(self, shopping_cart):
        # Test adding available items and calculating total
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.add_item("item2", 1) == True
        assert shopping_cart.get_total() == 40.0  # (2 * 10.0) + (1 * 20.0)

    def test_out_of_stock_handling(self, shopping_cart):
        # Test adding item with insufficient stock
        assert shopping_cart.add_item("item1", 6) == False  # Only 5 in stock
        assert shopping_cart.add_item("item3", 1) == False  # 0 in stock
        assert shopping_cart.get_total() == 0.0

    def test_invalid_item_handling(self, shopping_cart):
        # Test adding non-existent item
        assert shopping_cart.add_item("nonexistent", 1) == False
        assert shopping_cart.get_total() == 0.0

    def test_multiple_add_same_item(self, shopping_cart):
        # Test adding same item multiple times
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.get_total() == 40.0  # 4 * 10.0

    def test_mixed_valid_invalid_items(self, shopping_cart):
        # Test mixing valid and invalid operations
        assert shopping_cart.add_item("item1", 2) == True
        assert shopping_cart.add_item("nonexistent", 1) == False
        assert shopping_cart.add_item("item2", 1) == True
        assert shopping_cart.get_total() == 40.0  # (2 * 10.0) + (1 * 20.0)

    def test_edge_case_zero_quantity(self, shopping_cart):
        # Test adding zero quantity
        assert shopping_cart.add_item("item1", 0) == True
        assert shopping_cart.get_total() == 0.0