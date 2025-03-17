import pytest
from GradeBook import GradeBook
from StudentRegistry import StudentRegistry

class TestIntegration:
    @pytest.fixture
    def setup(self):
        grade_book = GradeBook()
        registry = StudentRegistry(grade_book)
        return registry, grade_book

    def test_register_student_and_add_grade(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        # Test student registration
        assert registry.register_student(student_id, "John Doe")
        assert student_id in registry.students
        
        # Test adding grade for registered student
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
        
        assert grade_book.get_average(student_id) == 90.0

    def test_unregistered_student_grade(self, setup):
        registry, grade_book = setup
        student_id = "99999"
        
        # Should not allow adding grades for unregistered students
        assert not registry.add_course_grade(student_id, "Math", 85)
        assert student_id not in grade_book.grades

    def test_duplicate_registration(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        assert registry.register_student(student_id, "John Doe")
        assert not registry.register_student(student_id, "Jane Doe")
        assert registry.students[student_id]["name"] == "John Doe"

    def test_grade_persistence(self, setup):
        registry, grade_book = setup
        student_id = "12345"
        
        registry.register_student(student_id, "Alice Brown")
        registry.add_course_grade(student_id, "Math", 95)
        registry.add_course_grade(student_id, "Math", 85)
        
        assert grade_book.grades[student_id]["Math"] == 85