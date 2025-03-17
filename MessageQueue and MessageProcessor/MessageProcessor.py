class MessageProcessor:
    def __init__(self, queue):
        self.queue = queue
        self.processed_messages = []
        
    def process_next(self):
        message = self.queue.get_next_message()
        if message:
            self.processed_messages.append(message.upper())
            return True
        return False
        
    def process_all(self):
        count = 0
        while self.process_next():
            count += 1
        return count