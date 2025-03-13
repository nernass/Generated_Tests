class NotificationService:
    def __init__(self):
        self.notifications = []
        
    def notify(self, message):
        self.notifications.append(message)
        return len(self.notifications)
        
    def get_latest(self):
        return self.notifications[-1] if self.notifications else None