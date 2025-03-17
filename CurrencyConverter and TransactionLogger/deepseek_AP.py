import pytest
from unittest.mock import MagicMock
from CurrencyConverter import CurrencyConverter
from TransactionLogger import TransactionLogger

class TestIntegrationCurrencyConverter:
    def setup_method(self):
        self.mock_logger = MagicMock(spec=TransactionLogger)
        self.converter = CurrencyConverter(self.mock_logger)

    def test_valid_conversion_and_logging(self):
        self.mock_logger.log_conversion.return_value = 1
        
        result = self.converter.convert("USD", "EUR", 100)
        
        assert result == 85.0
        self.mock_logger.log_conversion.assert_called_once_with("USD", "EUR", 100, 85.0)

    def test_logger_failure_propagation(self):
        self.mock_logger.log_conversion.side_effect = Exception("Logging service down")
        
        with pytest.raises(Exception) as exc_info:
            self.converter.convert("EUR", "GBP", 50)
        assert "Logging service down" in str(exc_info.value)

    def test_invalid_currency_handling(self):
        result = self.converter.convert("USD", "JPY", 200)
        
        assert result is None
        self.mock_logger.log_conversion.assert_not_called()

    def test_zero_amount_edge_case(self):
        self.mock_logger.log_conversion.return_value = 1
        
        result = self.converter.convert("GBP", "USD", 0)
        
        assert result == 0.0
        self.mock_logger.log_conversion.assert_called_once_with("GBP", "USD", 0, 0.0)

    def test_large_amount_conversion(self):
        self.mock_logger.log_conversion.return_value = 1
        
        result = self.converter.convert("USD", "EUR", 10**6)
        expected_result = round(10**6 * 0.85, 2)
        
        assert result == expected_result
        self.mock_logger.log_conversion.assert_called_once_with("USD", "EUR", 10**6, expected_result)

    def test_real_integration_flow(self):
        real_logger = TransactionLogger()
        converter = CurrencyConverter(real_logger)
        
        converter.convert("USD", "GBP", 100)
        assert len(real_logger.logs) == 1
        assert real_logger.logs[0]["result"] == 73.0