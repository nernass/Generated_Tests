import pytest
from StudentRegistry import StudentRegistry
from GradeBook import GradeBook

class TestIntegration:
    @pytest.fixture
    def setup(self):
        grade_book = GradeBook()
        registry = StudentRegistry(grade_book)
        return registry, grade_book

    def test_register_student_and_add_grade(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        # Register a student
        assert registry.register_student(student_id, "John Doe")
        assert student_id in registry.students
        assert registry.students[student_id]["name"] == "John Doe"
        
        # Add grade for the registered student
        assert registry.add_course_grade(student_id, "Math", 85)
        assert student_id in grade_book.grades
        assert grade_book.grades[student_id]["Math"] == 85

    def test_add_multiple_grades(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        registry.register_student(student_id, "Jane Smith")
        registry.add_course_grade(student_id, "Math", 90)
        registry.add_course_grade(student_id, "Physics", 85)
        registry.add_course_grade(student_id, "Chemistry", 95)
        
        assert len(grade_book.grades[student_id]) == 3
        assert grade_book.get_average(student_id) == 90.0

    def test_unregistered_student_grade(self, setup):
        registry, grade_book = setup
        student_id = "99999"
        
        # Attempt to add a grade for an unregistered student
        assert not registry.add_course_grade(student_id, "Math", 85)
        assert student_id not in grade_book.grades

    def test_duplicate_registration(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        assert registry.register_student(student_id, "John Doe")
        assert not registry.register_student(student_id, "Jane Doe")
        assert registry.students[student_id]["name"] == "John Doe"

    def test_update_existing_grade(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        registry.register_student(student_id, "Alice Brown")
        registry.add_course_grade(student_id, "Math", 95)
        registry.add_course_grade(student_id, "Math", 85)
        
        assert grade_book.grades[student_id]["Math"] == 85

    def test_multiple_students(self, setup):
        registry, grade_book = setup
        
        registry.register_student("001", "Student One")
        registry.register_student("002", "Student Two")
        
        registry.add_course_grade("001", "Math", 90)
        registry.add_course_grade("002", "Math", 80)
        
        assert grade_book.grades["001"]["Math"] == 90
        assert grade_book.grades["002"]["Math"] == 80
        
    def test_get_average_empty(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        registry.register_student(student_id, "Empty Student")
        average = grade_book.get_average(student_id)
        
        assert average is None
        
    def test_get_average_multiple_courses(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        registry.register_student(student_id, "Multi Course")
        registry.add_course_grade(student_id, "Math", 80)
        registry.add_course_grade(student_id, "Physics", 90)
        registry.add_course_grade(student_id, "Chemistry", 100)
        
        assert grade_book.get_average(student_id) == 90.0