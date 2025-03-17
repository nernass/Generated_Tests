class MessageQueue:
    def __init__(self):
        self.messages = []
        
    def add_message(self, message):
        self.messages.append(message)
        return True
        
    def get_next_message(self):
        if self.messages:
            return self.messages.pop(0)
        return None

