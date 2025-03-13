import pytest
from unittest.mock import MagicMock, mock_open
from Calculator import Calculator
from Logger import Logger

class TestIntegration:
    def setup_method(self):
        self.mock_logger = MagicMock(spec=Logger)
        self.mock_logger.log_file = "test.log"
        self.calculator = Calculator(self.mock_logger)

    def test_add_logs_correctly(self):
        result = self.calculator.add(5, 3)
        assert result == 8
        self.mock_logger.log.assert_called_once_with("Addition: 5 + 3 = 8")

    def test_subtract_logs_correctly(self):
        result = self.calculator.subtract(10, 4)
        assert result == 6
        self.mock_logger.log.assert_called_once_with("Subtraction: 10 - 4 = 6")

    def test_logger_error_propagates(self):
        self.mock_logger.log.side_effect = IOError("File write error")
        with pytest.raises(IOError):
            self.calculator.add(2, 2)
        self.mock_logger.log.assert_called_once()

    def test_edge_cases_logging(self):
        self.calculator.add(0, 0)
        self.mock_logger.log.assert_called_with("Addition: 0 + 0 = 0")
        
        self.calculator.subtract(-5, -3)
        self.mock_logger.log.assert_called_with("Subtraction: -5 - -3 = -2")

    def test_invalid_input_handling(self):
        with pytest.raises(TypeError):
            self.calculator.add("2", 3)
        self.mock_logger.log.assert_not_called()

        with pytest.raises(TypeError):
            self.calculator.subtract(5, "3")
        self.mock_logger.log.assert_not_called()

    def test_file_writing_integration(self):
        real_logger = Logger("test.log")
        calculator = Calculator(real_logger)
        with open("test.log", "r") as f:
            initial_content = f.read()
        
        calculator.add(7, 3)
        
        with open("test.log", "r") as f:
            new_content = f.read()
        assert new_content != initial_content
        assert "7 + 3 = 10" in new_content