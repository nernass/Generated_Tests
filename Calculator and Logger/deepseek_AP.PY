import pytest
from unittest.mock import MagicMock
from Calculator import Calculator
from Logger import Logger

class TestCalculatorIntegration:
    def setup_method(self):
        self.mock_logger = MagicMock(spec=Logger)
        self.calculator = Calculator(self.mock_logger)

    # Success path tests
    def test_add_success(self):
        result = self.calculator.add(2, 3)
        assert result == 5
        self.mock_logger.log.assert_called_once_with("Addition: 2 + 3 = 5")

    def test_subtract_success(self):
        result = self.calculator.subtract(5, 3)
        assert result == 2
        self.mock_logger.log.assert_called_once_with("Subtraction: 5 - 3 = 2")

    # Partial failure test
    def test_logger_failure_propagates(self):
        self.mock_logger.log.side_effect = Exception("Log write failed")
        with pytest.raises(Exception) as exc_info:
            self.calculator.add(2, 3)
        assert "Log write failed" in str(exc_info.value)
        self.mock_logger.log.assert_called_once()

    # Edge case tests
    def test_add_edge_cases(self):
        # Zero values
        result = self.calculator.add(0, 0)
        assert result == 0
        self.mock_logger.log.assert_called_once_with("Addition: 0 + 0 = 0")
        
        # Negative values
        self.mock_logger.reset_mock()
        result = self.calculator.add(-1, -2)
        assert result == -3
        self.mock_logger.log.assert_called_once_with("Addition: -1 + -2 = -3")

        # Large values
        self.mock_logger.reset_mock()
        large_num = 10**18
        result = self.calculator.add(large_num, large_num)
        assert result == 2 * large_num
        self.mock_logger.log.assert_called_once_with(f"Addition: {large_num} + {large_num} = {2*large_num}")

    # Invalid input test
    def test_invalid_input_handling(self):
        # Non-integer input
        with pytest.raises(TypeError):
            self.calculator.add("2", 3)
        self.mock_logger.log.assert_not_called()

        # Non-integer input for subtraction
        with pytest.raises(TypeError):
            self.calculator.subtract(5, "3")
        self.mock_logger.log.assert_not_called()