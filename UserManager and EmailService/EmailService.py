class EmailService:
    def __init__(self):
        self.sent_emails = []
        
    def send_welcome(self, email):
        message = f"Welcome to our service!"
        self.sent_emails.append({"to": email, "message": message})
        return True
        
    def get_sent_count(self):
        return len(self.sent_emails)