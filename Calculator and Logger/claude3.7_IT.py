import os
import pytest
from Calculator import Calculator
from Logger import Logger

class TestIntegration:
    @pytest.fixture
    def setup(self):
        # Create a temporary log file for testing
        test_log = "test_integration.log"
        
        # Clean up any existing test log
        if os.path.exists(test_log):
            os.remove(test_log)
            
        # Create logger and calculator instances
        logger = Logger(log_file=test_log)
        calculator = Calculator(logger)
        
        yield calculator, logger, test_log
        
        # Cleanup after test
        if os.path.exists(test_log):
            os.remove(test_log)
    
    def test_add_operation_logged(self, setup):
        calculator, logger, log_file = setup
        
        # Perform calculation
        result = calculator.add(5, 3)
        
        # Verify calculation result
        assert result == 8
        
        # Verify log content
        with open(log_file, 'r') as f:
            log_content = f.read()
            
        assert "Addition: 5 + 3 = 8" in log_content
    
    def test_subtract_operation_logged(self, setup):
        calculator, logger, log_file = setup
        
        # Perform calculation
        result = calculator.subtract(10, 4)
        
        # Verify calculation result
        assert result == 6
        
        # Verify log content
        with open(log_file, 'r') as f:
            log_content = f.read()
            
        assert "Subtraction: 10 - 4 = 6" in log_content
    
    def test_multiple_operations(self, setup):
        calculator, logger, log_file = setup
        
        # Perform multiple calculations
        add_result = calculator.add(7, 3)
        subtract_result = calculator.subtract(20, 5)
        
        # Verify calculation results
        assert add_result == 10
        assert subtract_result == 15
        
        # Verify log entries order and content
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
        
        assert len(log_lines) == 2
        assert "Addition: 7 + 3 = 10" in log_lines[0]
        assert "Subtraction: 20 - 5 = 15" in log_lines[1]
    
    def test_logger_initialization_with_custom_file(self, setup):
        # Ignore the fixture and create a new custom one
        custom_log = "custom_log.log"
        
        # Clean up any existing custom log
        if os.path.exists(custom_log):
            os.remove(custom_log)
            
        try:
            # Create logger with custom file and calculator
            custom_logger = Logger(log_file=custom_log)
            custom_calculator = Calculator(custom_logger)
            
            # Perform calculation
            result = custom_calculator.add(100, 50)
            
            # Verify log was written to custom file
            assert os.path.exists(custom_log)
            with open(custom_log, 'r') as f:
                log_content = f.read()
                
            assert "Addition: 100 + 50 = 150" in log_content
            
        finally:
            # Clean up
            if os.path.exists(custom_log):
                os.remove(custom_log)