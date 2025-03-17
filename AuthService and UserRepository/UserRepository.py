class UserRepository:
    def __init__(self):
        self.users = {
            "alice": {"password": "pass123", "role": "admin"},
            "bob": {"password": "pass456", "role": "user"}
        }
        
    def get_user(self, username):
        return self.users.get(username)
        
    def update_last_login(self, username):
        if username in self.users:
            self.users[username]["last_login"] = "2023-07-14"
            return True
        return False
