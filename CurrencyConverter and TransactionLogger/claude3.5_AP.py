import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from CurrencyConverter import CurrencyConverter
from TransactionLogger import TransactionLogger

class TestCurrencyConverterIntegration:
    @pytest.fixture
    def mock_logger(self):
        mock = Mock(spec=TransactionLogger)
        mock.log_conversion.return_value = 1
        return mock
    
    @pytest.fixture
    def real_logger(self):
        return TransactionLogger()
    
    @pytest.fixture
    def converter_with_mock(self, mock_logger):
        return CurrencyConverter(mock_logger)
    
    @pytest.fixture
    def converter_with_real(self, real_logger):
        return CurrencyConverter(real_logger)

    # Success Path Tests
    def test_successful_conversion_flow(self, converter_with_real, real_logger):
        result = converter_with_real.convert("USD", "EUR", 100)
        
        assert result == 85.00
        assert len(real_logger.logs) == 1
        assert real_logger.logs[0] == {
            "from": "USD",
            "to": "EUR",
            "amount": 100,
            "result": 85.00
        }

    def test_mock_logger_interaction(self, converter_with_mock, mock_logger):
        result = converter_with_mock.convert("USD", "GBP", 100)
        
        assert result == 73.00
        mock_logger.log_conversion.assert_called_once_with(
            "USD", "GBP", 100, 73.00
        )

    # Failure Path Tests
    def test_logger_failure(self, converter_with_mock, mock_logger):
        mock_logger.log_conversion.side_effect = Exception("Logging failed")
        
        with pytest.raises(Exception) as exc_info:
            converter_with_mock.convert("USD", "EUR", 100)
        
        assert str(exc_info.value) == "Logging failed"

    def test_invalid_currency_handling(self, converter_with_real, real_logger):
        result = converter_with_real.convert("USD", "XXX", 100)
        
        assert result is None
        assert len(real_logger.logs) == 0

    # Edge Cases
    @pytest.mark.parametrize("amount,expected", [
        (0, 0),
        (-100, -85.00),
        (999999.99, 849999.99),
        (0.01, 0.01)
    ])
    def test_boundary_values(self, converter_with_real, real_logger, amount, expected):
        result = converter_with_real.convert("USD", "EUR", amount)
        
        assert result == expected
        assert len(real_logger.logs) == 1
        assert real_logger.logs[0]["amount"] == amount
        assert real_logger.logs[0]["result"] == expected

    def test_multiple_conversions(self, converter_with_real, real_logger):
        conversions = [
            ("USD", "EUR", 100),
            ("EUR", "GBP", 50),
            ("GBP", "USD", 25)
        ]
        
        for from_curr, to_curr, amount in conversions:
            converter_with_real.convert(from_curr, to_curr, amount)
        
        assert len(real_logger.logs) == 3
        for i, (from_curr, to_curr, amount) in enumerate(conversions):
            assert real_logger.logs[i]["from"] == from_curr
            assert real_logger.logs[i]["to"] == to_curr
            assert real_logger.logs[i]["amount"] == amount

    @pytest.mark.parametrize("test_input", [None, "", float('inf'), float('nan')])
    def test_invalid_input_types(self, converter_with_real, real_logger, test_input):
        with pytest.raises((TypeError, ValueError)):
            converter_with_real.convert("USD", "EUR", test_input)
        
        assert len(real_logger.logs) == 0