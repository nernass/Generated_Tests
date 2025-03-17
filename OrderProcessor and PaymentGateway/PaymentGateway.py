class PaymentGateway:
    def __init__(self):
        self.transactions = []
        
    def process_payment(self, amount, card_number):
        if len(card_number) == 16 and card_number.isdigit():
            transaction_id = f"TX-{len(self.transactions) + 1}"
            self.transactions.append({"id": transaction_id, "amount": amount, "card": card_number[-4:]})
            return transaction_id
        return None

