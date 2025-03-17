class TransactionLogger:
    def __init__(self):
        self.logs = []
        
    def log_conversion(self, from_currency, to_currency, amount, result):
        self.logs.append({
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "result": result
        })
        return len(self.logs)

