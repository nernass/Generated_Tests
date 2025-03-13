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