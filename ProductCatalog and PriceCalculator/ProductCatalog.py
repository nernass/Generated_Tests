class ProductCatalog:
    def __init__(self, price_calculator):
        self.products = {
            "laptop": {"base_price": 1000, "category": "electronics"},
            "book": {"base_price": 20, "category": "media"}
        }
        self.price_calculator = price_calculator
        
    def get_product_price(self, product_id, apply_discount=False):
        if product_id in self.products:
            base_price = self.products[product_id]["base_price"]
            return self.price_calculator.calculate_final_price(base_price, apply_tax=True, apply_discount=apply_discount)
        return None