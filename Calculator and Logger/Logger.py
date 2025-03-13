from datetime import datetime

class Logger:
    def __init__(self, log_file="app.log"):
        self.log_file = log_file
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp}: {message}"
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
        return log_entry