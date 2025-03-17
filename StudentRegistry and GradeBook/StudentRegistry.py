class StudentRegistry:
    def __init__(self, grade_book):
        self.students = {}
        self.grade_book = grade_book
        
    def register_student(self, student_id, name):
        if student_id not in self.students:
            self.students[student_id] = {"name": name}
            return True
        return False
        
    def add_course_grade(self, student_id, course, grade):
        if student_id in self.students:
            return self.grade_book.add_grade(student_id, course, grade)
        return False