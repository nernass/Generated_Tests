class OrderProcessor:
    def __init__(self, payment_gateway):
        self.orders = {}
        self.payment_gateway = payment_gateway
        
    def create_order(self, items, total, card_number):
        transaction_id = self.payment_gateway.process_payment(total, card_number)
        if transaction_id:
            order_id = f"ORD-{len(self.orders) + 1}"
            self.orders[order_id] = {"items": items, "total": total, "transaction_id": transaction_id}
            return order_id
        return None