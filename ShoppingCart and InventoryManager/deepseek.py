import pytest
from unittest.mock import MagicMock
from InventoryManager import InventoryManager
from ShoppingCart import ShoppingCart

class TestIntegrationShoppingCart:
    def setup_method(self):
        self.mock_inventory = MagicMock(spec=InventoryManager)
        self.cart = ShoppingCart(self.mock_inventory)

    def test_valid_item_addition_and_total(self):
        self.mock_inventory.check_availability.return_value = True
        self.mock_inventory.get_price.return_value = 25
        
        assert self.cart.add_item("ITM001", 2) is True
        assert self.cart.get_total() == 50
        self.mock_inventory.check_availability.assert_called_once_with("ITM001", 2)
        self.mock_inventory.get_price.assert_called_once_with("ITM001")

    def test_unavailable_item_handling(self):
        self.mock_inventory.check_availability.return_value = False
        
        assert self.cart.add_item("ITM999", 5) is False
        assert self.cart.get_total() == 0
        self.mock_inventory.check_availability.assert_called_once_with("ITM999", 5)
        self.mock_inventory.get_price.assert_not_called()

    def test_inventory_error_propagation(self):
        self.mock_inventory.check_availability.side_effect = ValueError("Stock check failed")
        with pytest.raises(ValueError) as exc_info:
            self.cart.add_item("ITMERR", 1)
        assert "Stock check failed" in str(exc_info.value)

    def test_zero_quantity_edge_case(self):
        self.mock_inventory.check_availability.return_value = True
        
        assert self.cart.add_item("ITM002", 0) is True
        assert self.cart.get_total() == 0
        self.mock_inventory.check_availability.assert_called_once_with("ITM002", 0)

    def test_multiple_items_total_calculation(self):
        self.mock_inventory.check_availability.side_effect = [True, True]
        self.mock_inventory.get_price.side_effect = [10, 15]
        
        self.cart.add_item("ITM003")
        self.cart.add_item("ITM004", 3)
        assert self.cart.get_total() == (10 * 1 + 15 * 3)
        assert self.mock_inventory.get_price.call_count == 2

    def test_real_integration_with_inventory(self):
        real_inventory = InventoryManager()
        real_inventory.add_product("REAL001", 40, 10)
        real_cart = ShoppingCart(real_inventory)
        
        real_cart.add_item("REAL001", 3)
        assert real_cart.get_total() == 120
        real_cart.add_item("NONEXISTENT", 1)
        assert real_cart.get_total() == 120  # Failed addition shouldn't affect total