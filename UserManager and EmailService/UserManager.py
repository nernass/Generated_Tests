class UserManager:
    def __init__(self, email_service):
        self.users = {}
        self.email_service = email_service
        
    def create_user(self, user_id, email):
        if user_id in self.users:
            return False
        self.users[user_id] = {"email": email}
        self.email_service.send_welcome(email)
        return True