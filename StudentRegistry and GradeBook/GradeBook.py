class GradeBook:
    def __init__(self):
        self.grades = {}
        
    def add_grade(self, student_id, course, grade):
        if student_id not in self.grades:
            self.grades[student_id] = {}
        self.grades[student_id][course] = grade
        return True
        
    def get_average(self, student_id):
        if student_id in self.grades and self.grades[student_id]:
            total = sum(self.grades[student_id].values())
            return total / len(self.grades[student_id])
        return None

