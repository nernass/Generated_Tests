class TaskScheduler:
    def __init__(self, notification_service):
        self.tasks = {}
        self.notification_service = notification_service
        self.task_id_counter = 0
        
    def schedule_task(self, description, due_date):
        task_id = self.task_id_counter
        self.tasks[task_id] = {
            "description": description,
            "due_date": due_date,
            "completed": False
        }
        self.task_id_counter += 1
        self.notification_service.notify(f"New task scheduled: {description}")
        return task_id
        
    def complete_task(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id]["completed"] = True
            return True
        return False