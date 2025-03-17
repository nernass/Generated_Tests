import pytest
from unittest.mock import Mock, patch
import sys
import os
from CurrencyConverter import CurrencyConverter
from TransactionLogger import TransactionLogger

class TestCurrencyConverterIntegration:
    @pytest.fixture
    def real_logger(self):
        return TransactionLogger()
    
    @pytest.fixture
    def mock_logger(self):
        mock = Mock(spec=TransactionLogger)
        # Configure mock to return log count like the real logger
        mock.log_conversion.return_value = 1
        return mock
    
    @pytest.fixture
    def converter_with_real_logger(self, real_logger):
        return CurrencyConverter(real_logger)
    
    @pytest.fixture
    def converter_with_mock_logger(self, mock_logger):
        return CurrencyConverter(mock_logger)
    
    # === Success Path Tests ===
    def test_successful_conversion_end_to_end(self, converter_with_real_logger, real_logger):
        """Test successful end-to-end conversion with real components"""
        # Execute workflow
        result = converter_with_real_logger.convert("USD", "EUR", 100)
        
        # Assert conversion result
        assert result == 85.0
        
        # Assert logger received correct data
        assert len(real_logger.logs) == 1
        log_entry = real_logger.logs[0]
        assert log_entry["from"] == "USD"
        assert log_entry["to"] == "EUR"
        assert log_entry["amount"] == 100
        assert log_entry["result"] == 85.0
    
    def test_data_flow_accuracy(self, converter_with_mock_logger, mock_logger):
        """Test data flows correctly from converter to logger"""
        # Execute workflow
        result = converter_with_mock_logger.convert("USD", "GBP", 200)
        
        # Assert conversion result
        assert result == 146.0
        
        # Assert logger was called with correct parameters
        mock_logger.log_conversion.assert_called_once_with("USD", "GBP", 200, 146.0)
    
    # === Partial Failure Tests ===
    def test_logger_exception_handling(self, converter_with_mock_logger, mock_logger):
        """Test converter handles logger exceptions gracefully"""
        # Configure mock to raise exception
        mock_logger.log_conversion.side_effect = Exception("Database connection failed")
        
        # Execute workflow - this should raise the exception since converter doesn't catch it
        with pytest.raises(Exception) as excinfo:
            converter_with_mock_logger.convert("USD", "EUR", 100)
        
        # Assert exception details
        assert "Database connection failed" in str(excinfo.value)
    
    # === Edge Cases ===
    def test_negative_amount_handling(self, converter_with_real_logger, real_logger):
        """Test negative amount conversion"""
        # Execute workflow with negative amount
        result = converter_with_real_logger.convert("USD", "EUR", -50)
        
        # Assert conversion result (should handle negative numbers)
        assert result == -42.5
        
        # Assert logger received correct data
        assert len(real_logger.logs) == 1
        assert real_logger.logs[0]["amount"] == -50
        assert real_logger.logs[0]["result"] == -42.5
    
    def test_zero_amount_handling(self, converter_with_real_logger, real_logger):
        """Test zero amount conversion"""
        # Execute workflow with zero amount
        result = converter_with_real_logger.convert("EUR", "USD", 0)
        
        # Assert conversion result
        assert result == 0
        
        # Assert logger received correct data
        assert len(real_logger.logs) == 1
        assert real_logger.logs[0]["amount"] == 0
        assert real_logger.logs[0]["result"] == 0
    
    def test_invalid_currency_handling(self, converter_with_real_logger, real_logger):
        """Test invalid currency handling"""
        # Execute workflow with invalid currency
        result = converter_with_real_logger.convert("USD", "JPY", 100)
        
        # Assert conversion result is None for invalid currency
        assert result is None
        
        # Assert no log entry was created
        assert len(real_logger.logs) == 0
    
    def test_large_amount_handling(self, converter_with_real_logger, real_logger):
        """Test large amount conversion"""
        # Execute workflow with large amount
        large_amount = 1000000000
        result = converter_with_real_logger.convert("USD", "EUR", large_amount)
        
        # Assert conversion result
        assert result == 850000000.0
        
        # Assert logger received correct data
        assert len(real_logger.logs) == 1
        assert real_logger.logs[0]["amount"] == large_amount
        assert real_logger.logs[0]["result"] == 850000000.0
    
    def test_multiple_conversions(self, converter_with_real_logger, real_logger):
        """Test multiple conversions are logged correctly"""
        # Execute multiple conversions
        converter_with_real_logger.convert("USD", "EUR", 100)
        converter_with_real_logger.convert("EUR", "GBP", 50)
        converter_with_real_logger.convert("GBP", "USD", 25)
        
        # Assert all conversions were logged
        assert len(real_logger.logs) == 3
        
        # Verify log entries
        assert real_logger.logs[0]["from"] == "USD" and real_logger.logs[0]["to"] == "EUR"
        assert real_logger.logs[1]["from"] == "EUR" and real_logger.logs[1]["to"] == "GBP"
        assert real_logger.logs[2]["from"] == "GBP" and real_logger.logs[2]["to"] == "USD"