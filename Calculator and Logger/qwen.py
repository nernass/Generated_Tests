import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Calculator and Logger classes
class Calculator:
    def __init__(self, logger):
        self.logger = logger

    def add(self, a, b):
        result = a + b
        self.logger.log(f"Addition: {a} + {b} = {result}")
        return result
        
    def subtract(self, a, b):
        result = a - b
        self.logger.log(f"Subtraction: {a} - {b} = {result}")
        return result

class Logger:
    def __init__(self, log_file="app.log"):
        self.log_file = log_file

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp}: {message}"
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
        return log_entry

# Test class
class TestCalculatorIntegration:
    @patch('__main__.Logger')
    def test_success_path_addition(self, MockLogger):
        # Arrange
        mock_logger = MockLogger()
        calculator = Calculator(mock_logger)
        
        # Act
        result = calculator.add(5, 3)
        
        # Assert
        assert result == 8
        mock_logger.log.assert_called_once_with("Addition: 5 + 3 = 8")

    @patch('__main__.Logger')
    def test_success_path_subtraction(self, MockLogger):
        # Arrange
        mock_logger = MockLogger()
        calculator = Calculator(mock_logger)
        
        # Act
        result = calculator.subtract(5, 3)
        
        # Assert
        assert result == 2
        mock_logger.log.assert_called_once_with("Subtraction: 5 - 3 = 2")

    @patch('__main__.Logger')
    def test_failure_path_addition(self, MockLogger):
        # Arrange
        mock_logger = MockLogger()
        mock_logger.log.side_effect = Exception("Logging failed")
        calculator = Calculator(mock_logger)
        
        # Act & Assert
        with pytest.raises(Exception) as e:
            calculator.add(5, 3)
        assert str(e.value) == "Logging failed"

    @patch('__main__.Logger')
    def test_failure_path_subtraction(self, MockLogger):
        # Arrange
        mock_logger = MockLogger()
        mock_logger.log.side_effect = Exception("Logging failed")
        calculator = Calculator(mock_logger)
        
        # Act & Assert
        with pytest.raises(Exception) as e:
            calculator.subtract(5, 3)
        assert str(e.value) == "Logging failed"

    @patch('__main__.Logger')
    def test_edge_case_addition_zero(self, MockLogger):
        # Arrange
        mock_logger = MockLogger()
        calculator = Calculator(mock_logger)
        
        # Act
        result = calculator.add(0, 0)
        
        # Assert
        assert result == 0
        mock_logger.log.assert_called_once_with("Addition: 0 + 0 = 0")

    @patch('__main__.Logger')
    def test_edge_case_subtraction_negative(self, MockLogger):
        # Arrange
        mock_logger = MockLogger()
        calculator = Calculator(mock_logger)
        
        # Act
        result = calculator.subtract(0, 5)
        
        # Assert
        assert result == -5
        mock_logger.log.assert_called_once_with("Subtraction: 0 - 5 = -5")