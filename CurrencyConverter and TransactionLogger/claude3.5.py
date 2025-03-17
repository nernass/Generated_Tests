import pytest
from CurrencyConverter import CurrencyConverter
from TransactionLogger import TransactionLogger

def test_currency_conversion_with_logging():
    # Setup
    logger = TransactionLogger()
    converter = CurrencyConverter(logger)
    
    # Test conversion with logging
    result = converter.convert("USD", "EUR", 100)
    
    # Verify conversion result
    assert result == 85.00
    
    # Verify log entry
    assert len(logger.logs) == 1
    assert logger.logs[0]["from"] == "USD"
    assert logger.logs[0]["to"] == "EUR"
    assert logger.logs[0]["amount"] == 100
    assert logger.logs[0]["result"] == 85.00

def test_multiple_conversions_logging():
    logger = TransactionLogger()
    converter = CurrencyConverter(logger)
    
    # Perform multiple conversions
    converter.convert("USD", "EUR", 50)
    converter.convert("EUR", "GBP", 100)
    converter.convert("GBP", "USD", 75)
    
    # Verify log entries
    assert len(logger.logs) == 3
    
    # Check specific log details
    first_log = logger.logs[0]
    assert first_log["from"] == "USD"
    assert first_log["to"] == "EUR"
    assert first_log["amount"] == 50
    
def test_invalid_currency_logging():
    logger = TransactionLogger()
    converter = CurrencyConverter(logger)
    
    # Test invalid currency conversion
    result = converter.convert("USD", "JPY", 100)
    
    # Verify conversion failed
    assert result is None
    
    # Verify no log entry was created
    assert len(logger.logs) == 0