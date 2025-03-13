import os
import pytest
import tempfile
import re
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
from Calculator import Calculator
from Logger import Logger

class TestIntegration:
    @pytest.fixture
    def setup(self):
        # Create a temporary log file for testing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as temp:
            test_log_path = temp.name
        
        # Setup components
        logger = Logger(log_file=test_log_path)
        calculator = Calculator(logger)
        
        yield calculator, logger, test_log_path
        
        # Cleanup
        if os.path.exists(test_log_path):
            os.remove(test_log_path)
    
    # Success Path: Normal Operation Tests
    def test_add_operation_success_path(self, setup):
        # Arrange
        calculator, logger, log_path = setup
        a, b = 10, 5
        expected_result = 15
        
        # Act
        result = calculator.add(a, b)
        
        # Assert
        assert result == expected_result
        
        with open(log_path, 'r') as log_file:
            log_content = log_file.read()
            
        # Verify correct log entry was written
        assert f"Addition: {a} + {b} = {result}" in log_content
        # Verify timestamp format is correct
        assert re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', log_content)
    
    def test_subtract_operation_success_path(self, setup):
        # Arrange
        calculator, logger, log_path = setup
        a, b = 20, 8
        expected_result = 12
        
        # Act
        result = calculator.subtract(a, b)
        
        # Assert
        assert result == expected_result
        
        with open(log_path, 'r') as log_file:
            log_content = log_file.read()
            
        # Verify correct log entry was written
        assert f"Subtraction: {a} - {b} = {result}" in log_content
    
    def test_sequential_operations(self, setup):
        # Arrange
        calculator, logger, log_path = setup
        
        # Act - Perform multiple operations in sequence
        add_result = calculator.add(15, 5)
        subtract_result = calculator.subtract(add_result, 10)
        
        # Assert
        assert add_result == 20
        assert subtract_result == 10
        
        # Verify log entries in correct order
        with open(log_path, 'r') as log_file:
            log_lines = log_file.readlines()
            
        assert len(log_lines) == 2
        assert "Addition: 15 + 5 = 20" in log_lines[0]
        assert "Subtraction: 20 - 10 = 10" in log_lines[1]
    
    # Partial Failure: Logger Failure Tests
    def test_logger_write_failure(self, setup):
        # Arrange
        calculator, logger, _ = setup
        
        # Mock logger's open method to raise an exception
        with patch('builtins.open', side_effect=IOError("Cannot write to log file")):
            # Act & Assert
            with pytest.raises(IOError, match="Cannot write to log file"):
                calculator.add(10, 5)
    
    def test_logger_partial_write_failure(self, setup):
        # Arrange
        calculator, logger, _ = setup
        
        # Create a mock file handler that raises exception after write
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.write.side_effect = [None, IOError("Write interrupted")]
        
        # Act & Assert
        with patch('builtins.open', return_value=mock_file):
            with pytest.raises(IOError, match="Write interrupted"):
                calculator.add(10, 5)
    
    # Edge Cases
    def test_edge_case_large_numbers(self, setup):
        # Arrange
        calculator, logger, log_path = setup
        large_a = 10**10
        large_b = 10**9
        
        # Act
        result = calculator.add(large_a, large_b)
        
        # Assert
        assert result == 10**10 + 10**9
        
        with open(log_path, 'r') as log_file:
            log_content = log_file.read()
            
        assert f"Addition: {large_a} + {large_b} = {result}" in log_content
    
    def test_edge_case_negative_numbers(self, setup):
        # Arrange
        calculator, logger, log_path = setup
        
        # Act
        result = calculator.subtract(-30, 15)
        
        # Assert
        assert result == -45
        
        with open(log_path, 'r') as log_file:
            log_content = log_file.read()
            
        assert "Subtraction: -30 - 15 = -45" in log_content
    
    def test_custom_log_file_location(self):
        # Arrange
        custom_log = "./custom_directory/test.log"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(custom_log), exist_ok=True)
        
        if os.path.exists(custom_log):
            os.remove(custom_log)
        
        try:
            # Act
            logger = Logger(log_file=custom_log)
            calculator = Calculator(logger)
            result = calculator.add(7, 8)
            
            # Assert
            assert result == 15
            assert os.path.exists(custom_log)
            
            with open(custom_log, 'r') as log_file:
                log_content = log_file.read()
                
            assert "Addition: 7 + 8 = 15" in log_content
        finally:
            # Cleanup
            if os.path.exists(custom_log):
                os.remove(custom_log)
            
            # Try to remove directory if empty
            try:
                os.rmdir(os.path.dirname(custom_log))
            except:
                pass
    
    def test_data_flow_accuracy(self, setup):
        # Arrange
        calculator, logger, _ = setup
        
        # Spy on logger's log method
        with patch.object(logger, 'log', wraps=logger.log) as mock_log:
            # Act
            result = calculator.add(25, 17)
            
            # Assert
            assert result == 42
            
            # Verify the calculator passed the correct data to the logger
            mock_log.assert_called_once_with("Addition: 25 + 17 = 42")