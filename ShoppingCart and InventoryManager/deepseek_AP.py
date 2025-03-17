import pytest
from unittest.mock import MagicMock
from InventoryManager import InventoryManager
from ShoppingCart import ShoppingCart

class TestIntegrationInventoryShopping:
    def setup_method(self):
        self.mock_inventory = MagicMock(spec=InventoryManager)
        self.cart = ShoppingCart(self.mock_inventory)

    def test_successful_add_and_total(self):
        self.mock_inventory.check_availability.return_value = True
        self.mock_inventory.get_price.return_value = 50
        
        assert self.cart.add_item("item123", 3) is True
        assert self.cart.get_total() == 150
        self.mock_inventory.check_availability.assert_called_once_with("item123", 3)
        self.mock_inventory.get_price.assert_called_once_with("item123")

    def test_inventory_failure_blocks_add(self):
        self.mock_inventory.check_availability.return_value = False
        
        assert self.cart.add_item("item456", 5) is False
        assert self.cart.get_total() == 0
        self.mock_inventory.check_availability.assert_called_once_with("item456", 5)
        self.mock_inventory.get_price.assert_not_called()

    def test_edge_case_zero_quantity(self):
        self.mock_inventory.check_availability.return_value = True
        
        assert self.cart.add_item("item789", 0) is True
        assert self.cart.get_total() == 0
        self.mock_inventory.check_availability.assert_called_once_with("item789", 0)

    def test_nonexistent_item_total(self):
        self.mock_inventory.check_availability.return_value = True
        self.mock_inventory.get_price.return_value = 0
        
        self.cart.add_item("ghost_item")
        assert self.cart.get_total() == 0
        self.mock_inventory.get_price.assert_called_once_with("ghost_item")

    def test_multiple_items_calculation(self):
        self.mock_inventory.check_availability.side_effect = [True, True]
        self.mock_inventory.get_price.side_effect = [20, 30]
        
        self.cart.add_item("item1", 2)
        self.cart.add_item("item2", 1)
        assert self.cart.get_total() == (20*2 + 30*1)
        assert self.mock_inventory.get_price.call_count == 2

    def test_inventory_exception_handling(self):
        self.mock_inventory.check_availability.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception) as exc_info:
            self.cart.add_item("item999", 1)
        assert "DB Error" in str(exc_info.value)
        self.mock_inventory.check_availability.assert_called_once()