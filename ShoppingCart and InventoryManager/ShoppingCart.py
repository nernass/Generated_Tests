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