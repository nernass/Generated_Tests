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