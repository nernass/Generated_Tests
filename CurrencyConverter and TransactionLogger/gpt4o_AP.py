import pytest
from unittest.mock import Mock, patch
from CurrencyConverter import CurrencyConverter
from TransactionLogger import TransactionLogger

@pytest.fixture
def mock_logger():
    return Mock(spec=TransactionLogger)

@pytest.fixture
def converter(mock_logger):
    return CurrencyConverter(mock_logger)

def test_currency_conversion_with_logging(converter, mock_logger):
    # Test success path
    result = converter.convert("USD", "EUR", 100)
    
    # Assert final output
    assert result == 85.00
    
    # Assert data flow accuracy
    mock_logger.log_conversion.assert_called_once_with("USD", "EUR", 100, 85.00)

def test_conversion_with_invalid_currency(converter, mock_logger):
    # Test edge case: invalid currency
    result = converter.convert("USD", "JPY", 100)
    
    # Assert final output
    assert result is None
    
    # Assert no log entry created
    mock_logger.log_conversion.assert_not_called()

def test_partial_failure_logging(converter, mock_logger):
    # Mock logger to throw an exception
    mock_logger.log_conversion.side_effect = Exception("Logging failed")
    
    # Test partial failure
    result = converter.convert("USD", "EUR", 100)
    
    # Assert final output
    assert result == 85.00
    
    # Assert error handling
    mock_logger.log_conversion.assert_called_once_with("USD", "EUR", 100, 85.00)

def test_edge_case_zero_amount(converter, mock_logger):
    # Test edge case: zero amount
    result = converter.convert("USD", "EUR", 0)
    
    # Assert final output
    assert result == 0.00
    
    # Assert data flow accuracy
    mock_logger.log_conversion.assert_called_once_with("USD", "EUR", 0, 0.00)

def test_edge_case_large_amount(converter, mock_logger):
    # Test edge case: large amount
    result = converter.convert("USD", "EUR", 1000000)
    
    # Assert final output
    assert result == 850000.00
    
    # Assert data flow accuracy
    mock_logger.log_conversion.assert_called_once_with("USD", "EUR", 1000000, 850000.00)