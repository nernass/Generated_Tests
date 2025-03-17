class FormHandler:
    def __init__(self, validator):
        self.validator = validator
        self.submitted_data = {}
        
    def submit_form(self, email, password):
        if not self.validator.validate_email(email):
            return {"success": False, "errors": self.validator.error_messages}
            
        if not self.validator.validate_password(password):
            return {"success": False, "errors": self.validator.error_messages}
            
        self.submitted_data = {"email": email, "password": password}
        return {"success": True}