class AuthService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
        self.logged_in_users = []
        
    def login(self, username, password):
        user = self.user_repository.get_user(username)
        if user and user["password"] == password:
            self.logged_in_users.append(username)
            self.user_repository.update_last_login(username)
            return True
        return False