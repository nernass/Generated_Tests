import pytest
from unittest.mock import MagicMock

class InventoryManager:
    def __init__(self):
        self.inventory = {}

    def add_product(self, item_id, price, stock):
        self.inventory[item_id] = {"price": price, "stock": stock}

    def check_availability(self, item_id, quantity):
        if item_id not in self.inventory:
            return False
        return self.inventory[item_id]["stock"] >= quantity

    def get_price(self, item_id):
        if item_id in self.inventory:
            return self.inventory[item_id]["price"]
        return 0

class ShoppingCart:
    def __init__(self, inventory_manager):
        self.inventory = inventory_manager
        self.items = {}

    def add_item(self, item_id, quantity=1):
        if not self.inventory.check_availability(item_id, quantity):
            return False

        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
        return True

    def get_total(self):
        total = 0
        for item_id, quantity in self.items.items():
            price = self.inventory.get_price(item_id)
            total += price * quantity
        return total

@pytest.fixture
def inventory_manager():
    im = InventoryManager()
    im.add_product('item1', 10.0, 5)
    im.add_product('item2', 20.0, 3)
    return im

@pytest.fixture
def shopping_cart(inventory_manager):
    return ShoppingCart(inventory_manager)

class TestIntegrationInventoryManagerAndShoppingCart:

    def test_success_path_add_items_and_get_total(self, shopping_cart):
        shopping_cart.add_item('item1', 2)
        shopping_cart.add_item('item2', 1)
        assert shopping_cart.get_total() == 40.0

    def test_partial_failure_item_not_available(self, shopping_cart):
        assert shopping_cart.add_item('item1', 6) == False
        assert shopping_cart.get_total() == 0.0

    def test_partial_failure_item_does_not_exist(self, shopping_cart):
        assert shopping_cart.add_item('item3', 1) == False
        assert shopping_cart.get_total() == 0.0

    def test_edge_case_add_zero_quantity(self, shopping_cart):
        assert shopping_cart.add_item('item1', 0) == True
        assert shopping_cart.get_total() == 0.0

    def test_edge_case_add_max_quantity(self, shopping_cart):
        shopping_cart.add_item('item2', 3)
        assert shopping_cart.get_total() == 60.0
        assert shopping_cart.add_item('item2', 1) == False

    def test_inventory_manager_check_availability_mocked(self, shopping_cart, inventory_manager):
        inventory_manager.check_availability = MagicMock(return_value=False)
        assert shopping_cart.add_item('item1', 1) == False

    def test_inventory_manager_get_price_mocked(self, shopping_cart, inventory_manager):
        inventory_manager.get_price = MagicMock(return_value=0)
        shopping_cart.add_item('item1', 1)
        assert shopping_cart.get_total() == 0.0

    def test_shopping_cart_add_item_exception_handling(self, shopping_cart, inventory_manager):
        inventory_manager.check_availability = MagicMock(side_effect=Exception("Check availability failed"))
        with pytest.raises(Exception) as excinfo:
            shopping_cart.add_item('item1', 1)
        assert str(excinfo.value) == "Check availability failed"

    def test_shopping_cart_get_total_exception_handling(self, shopping_cart, inventory_manager):
        inventory_manager.get_price = MagicMock(side_effect=Exception("Get price failed"))
        shopping_cart.add_item('item1', 1)
        with pytest.raises(Exception) as excinfo:
            shopping_cart.get_total()
        assert str(excinfo.value) == "Get price failed"