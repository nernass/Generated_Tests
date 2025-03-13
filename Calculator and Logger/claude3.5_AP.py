import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from Calculator import Calculator
from Logger import Logger

class TestIntegration:
    @pytest.fixture
    def setup(self):
        test_log = "test_integration.log"
        if os.path.exists(test_log):
            os.remove(test_log)
            
        logger = Logger(log_file=test_log)
        calculator = Calculator(logger)
        
        yield calculator, logger, test_log
        
        if os.path.exists(test_log):
            os.remove(test_log)

    # Scenario 1: Success Path - Valid Input
    def test_successful_operation_flow(self, setup):
        calculator, logger, log_file = setup
        
        # Test calculator operations
        add_result = calculator.add(10, 5)
        subtract_result = calculator.subtract(20, 8)
        
        # Verify results
        assert add_result == 15
        assert subtract_result == 12
        
        # Verify log entries
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
            assert len(log_lines) == 2
            assert all(datetime.now().strftime("%Y-%m-%d") in line for line in log_lines)
            assert "Addition: 10 + 5 = 15" in log_lines[0]
            assert "Subtraction: 20 - 8 = 12" in log_lines[1]

    # Scenario 2: Failure Path - Logger Component Fails
    def test_logger_failure_handling(self, setup):
        calculator, logger, _ = setup
        
        # Mock logger to raise exception
        with patch.object(logger, 'log', side_effect=IOError("Failed to write to log")):
            # Verify calculator handles logger failure
            with pytest.raises(IOError) as exc_info:
                calculator.add(10, 5)
            assert "Failed to write to log" in str(exc_info.value)

    # Scenario 3: Invalid Input Handling
    def test_invalid_input_handling(self, setup):
        calculator, logger, log_file = setup
        
        # Test with non-numeric input
        with patch.object(logger, 'log') as mock_log:
            with pytest.raises(TypeError):
                calculator.add("invalid", 5)
            
            # Verify logger wasn't called with invalid input
            mock_log.assert_not_called()

    # Edge Cases Testing
    def test_edge_cases(self, setup):
        calculator, _, log_file = setup
        
        # Test boundary values
        max_result = calculator.add(float('inf'), 1)
        assert max_result == float('inf')
        
        zero_result = calculator.add(0, 0)
        assert zero_result == 0
        
        negative_result = calculator.subtract(-10, 5)
        assert negative_result == -15
        
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "Addition: inf + 1 = inf" in log_content
            assert "Addition: 0 + 0 = 0" in log_content
            assert "Subtraction: -10 - 5 = -15" in log_content

    # Data Flow Testing
    def test_data_flow_between_components(self, setup):
        calculator, logger, log_file = setup
        
        # Spy on logger's log method
        with patch.object(logger, 'log', wraps=logger.log) as logger_spy:
            # Perform calculation
            result = calculator.add(15, 25)
            
            # Verify correct data flow
            assert result == 40
            logger_spy.assert_called_once_with("Addition: 15 + 25 = 40")
            
            # Verify log file contains correct entry
            with open(log_file, 'r') as f:
                log_content = f.read()
                assert "Addition: 15 + 25 = 40" in log_content

    # File System Integration Testing
    def test_log_file_handling(self, setup):
        calculator, logger, log_file = setup
        
        # Test file creation
        assert os.path.exists(log_file)
        
        # Test file append behavior
        calculator.add(1, 1)
        calculator.add(2, 2)
        
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
            assert len(log_lines) == 2
            
        # Test file write permissions
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError):
                calculator.add(3, 3)