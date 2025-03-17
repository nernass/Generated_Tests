class PriceCalculator:
    def __init__(self):
        self.tax_rate = 0.1
        self.discount_rate = 0.05
        
    def calculate_final_price(self, base_price, apply_tax=True, apply_discount=False):
        price = base_price
        if apply_tax:
            price += base_price * self.tax_rate
        if apply_discount:
            price -= base_price * self.discount_rate
        return round(price, 2)

