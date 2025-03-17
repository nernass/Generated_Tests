import pytest
from unittest.mock import MagicMock

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

@pytest.fixture
def transaction_logger():
    return TransactionLogger()

@pytest.fixture
def currency_converter(transaction_logger):
    return CurrencyConverter(transaction_logger)

class TestIntegrationCurrencyConverterAndTransactionLogger:

    def test_success_path_convert_and_log(self, currency_converter, transaction_logger):
        result = currency_converter.convert("USD", "EUR", 100)
        assert result == 85.0
        assert len(transaction_logger.logs) == 1
        assert transaction_logger.logs[0] == {
            "from": "USD",
            "to": "EUR",
            "amount": 100,
            "result": 85.0
        }

    def test_partial_failure_invalid_from_currency(self, currency_converter, transaction_logger):
        result = currency_converter.convert("XYZ", "EUR", 100)
        assert result is None
        assert len(transaction_logger.logs) == 0

    def test_partial_failure_invalid_to_currency(self, currency_converter, transaction_logger):
        result = currency_converter.convert("USD", "XYZ", 100)
        assert result is None
        assert len(transaction_logger.logs) == 0

    def test_partial_failure_both_currencies_invalid(self, currency_converter, transaction_logger):
        result = currency_converter.convert("XYZ", "ABC", 100)
        assert result is None
        assert len(transaction_logger.logs) == 0

    def test_partial_failure_logger_fails(self, currency_converter, transaction_logger):
        transaction_logger.log_conversion = MagicMock(side_effect=Exception("Logging failed"))
        with pytest.raises(Exception) as excinfo:
            currency_converter.convert("USD", "EUR", 100)
        assert str(excinfo.value) == "Logging failed"
        assert len(transaction_logger.logs) == 0

    def test_edge_case_convert_zero_amount(self, currency_converter, transaction_logger):
        result = currency_converter.convert("USD", "EUR", 0)
        assert result == 0.0
        assert len(transaction_logger.logs) == 1
        assert transaction_logger.logs[0] == {
            "from": "USD",
            "to": "EUR",
            "amount": 0,
            "result": 0.0
        }

    def test_edge_case_convert_large_amount(self, currency_converter, transaction_logger):
        result = currency_converter.convert("USD", "EUR", 1000000)
        assert result == 850000.0
        assert len(transaction_logger.logs) == 1
        assert transaction_logger.logs[0] == {
            "from": "USD",
            "to": "EUR",
            "amount": 1000000,
            "result": 850000.0
        }

    def test_edge_case_convert_negative_amount(self, currency_converter, transaction_logger):
        result = currency_converter.convert("USD", "EUR", -100)
        assert result is None
        assert len(transaction_logger.logs) == 0