class CurrencyConverter:
    def __init__(self, logger):
        self.rates = {"USD": 1.0, "EUR": 0.85, "GBP": 0.73}
        self.logger = logger
        
    def convert(self, from_currency, to_currency, amount):
        if from_currency in self.rates and to_currency in self.rates:
            result = amount * (self.rates[to_currency] / self.rates[from_currency])
            self.logger.log_conversion(from_currency, to_currency, amount, result)
            return round(result, 2)
        return None