import os
import pytest
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
    
    def test_add_operation_integration(self, setup):
        calculator, _, log_file = setup
        result = calculator.add(10, 5)
        
        assert result == 15
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "Addition: 10 + 5 = 15" in log_content
            assert datetime.now().strftime("%Y-%m-%d") in log_content
    
    def test_subtract_operation_integration(self, setup):
        calculator, _, log_file = setup
        result = calculator.subtract(20, 8)
        
        assert result == 12
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "Subtraction: 20 - 8 = 12" in log_content
            assert datetime.now().strftime("%Y-%m-%d") in log_content
    
    def test_multiple_operations_sequence(self, setup):
        calculator, _, log_file = setup
        
        add_result = calculator.add(15, 5)
        subtract_result = calculator.subtract(add_result, 10)
        
        assert add_result == 20
        assert subtract_result == 10
        
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
            assert len(log_lines) == 2
            assert "Addition: 15 + 5 = 20" in log_lines[0]
            assert "Subtraction: 20 - 10 = 10" in log_lines[1]
    
    def test_logger_file_creation(self, setup):
        calculator, logger, log_file = setup
        
        assert os.path.exists(log_file)
        calculator.add(1, 1)
        
        file_stats = os.stat(log_file)
        assert file_stats.st_size > 0
    
    def test_calculator_with_custom_log_file(self):
        custom_log = "custom_test.log"
        if os.path.exists(custom_log):
            os.remove(custom_log)
        
        try:
            logger = Logger(log_file=custom_log)
            calculator = Calculator(logger)
            
            calculator.add(100, 200)
            assert os.path.exists(custom_log)
            
            with open(custom_log, 'r') as f:
                log_content = f.read()
                assert "Addition: 100 + 200 = 300" in log_content
        
        finally:
            if os.path.exists(custom_log):
                os.remove(custom_log)