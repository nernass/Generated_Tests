import pytest

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

def test_success_path_add_items_and_get_total(shopping_cart):
    shopping_cart.add_item('item1', 2)
    shopping_cart.add_item('item2', 1)
    assert shopping_cart.get_total() == 40.0

def test_partial_failure_item_not_available(shopping_cart):
    assert shopping_cart.add_item('item1', 6) == False
    assert shopping_cart.get_total() == 0.0

def test_partial_failure_item_does_not_exist(shopping_cart):
    assert shopping_cart.add_item('item3', 1) == False
    assert shopping_cart.get_total() == 0.0

def test_edge_case_add_zero_quantity(shopping_cart):
    assert shopping_cart.add_item('item1', 0) == True
    assert shopping_cart.get_total() == 0.0

def test_edge_case_add_max_quantity(shopping_cart):
    shopping_cart.add_item('item2', 3)
    assert shopping_cart.get_total() == 60.0
    assert shopping_cart.add_item('item2', 1) == False