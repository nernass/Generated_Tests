class DataValidator:
    def __init__(self):
        self.error_messages = []
        
    def validate_email(self, email):
        self.error_messages = []
        if not email or '@' not in email:
            self.error_messages.append("Invalid email format")
            return False
        return True
        
    def validate_password(self, password):
        self.error_messages = []
        if not password or len(password) < 8:
            self.error_messages.append("Password must be at least 8 characters")
            return False
        return True
