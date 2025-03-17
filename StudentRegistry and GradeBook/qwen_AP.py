import pytest
from unittest.mock import MagicMock

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

@pytest.fixture
def grade_book():
    return GradeBook()

@pytest.fixture
def student_registry(grade_book):
    return StudentRegistry(grade_book)

class TestIntegrationGradeBookAndStudentRegistry:

    def test_success_path_register_student_and_add_grade(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("student1", "Math", 90)
        assert result == True
        assert grade_book.grades == {"student1": {"Math": 90}}

    def test_success_path_register_student_and_add_multiple_grades(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        student_registry.add_course_grade("student1", "Math", 90)
        student_registry.add_course_grade("student1", "Science", 85)
        assert grade_book.grades == {"student1": {"Math": 90, "Science": 85}}

    def test_partial_failure_student_not_registered(self, student_registry, grade_book):
        result = student_registry.add_course_grade("student1", "Math", 90)
        assert result == False
        assert grade_book.grades == {}

    def test_partial_failure_grade_book_add_grade_fails(self, student_registry, grade_book):
        grade_book.add_grade = MagicMock(return_value=False)
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("student1", "Math", 90)
        assert result == False
        assert grade_book.grades == {}

    def test_partial_failure_grade_book_add_grade_raises_exception(self, student_registry, grade_book):
        grade_book.add_grade = MagicMock(side_effect=Exception("GradeBook error"))
        student_registry.register_student("student1", "Alice")
        with pytest.raises(Exception) as excinfo:
            student_registry.add_course_grade("student1", "Math", 90)
        assert str(excinfo.value) == "GradeBook error"
        assert grade_book.grades == {}

    def test_edge_case_register_student_with_empty_id(self, student_registry, grade_book):
        result = student_registry.register_student("", "Alice")
        assert result == False
        assert grade_book.grades == {}

    def test_edge_case_register_student_with_empty_name(self, student_registry, grade_book):
        result = student_registry.register_student("student1", "")
        assert result == True
        assert grade_book.grades == {}

    def test_edge_case_add_grade_with_empty_student_id(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("", "Math", 90)
        assert result == False
        assert grade_book.grades == {}

    def test_edge_case_add_grade_with_empty_course(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("student1", "", 90)
        assert result == True
        assert grade_book.grades == {"student1": {"": 90}}

    def test_edge_case_add_grade_with_invalid_grade(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("student1", "Math", "A")
        assert result == True
        assert grade_book.grades == {"student1": {"Math": "A"}}

    def test_edge_case_add_grade_with_large_grade_value(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("student1", "Math", 1000)
        assert result == True
        assert grade_book.grades == {"student1": {"Math": 1000}}

    def test_edge_case_add_grade_with_negative_grade_value(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("student1", "Math", -10)
        assert result == True
        assert grade_book.grades == {"student1": {"Math": -10}}

    def test_edge_case_add_grade_with_large_student_id(self, student_registry, grade_book):
        large_student_id = "a" * 100
        student_registry.register_student(large_student_id, "Alice")
        result = student_registry.add_course_grade(large_student_id, "Math", 90)
        assert result == True
        assert grade_book.grades == {large_student_id: {"Math": 90}}

    def test_edge_case_add_grade_with_large_course_name(self, student_registry, grade_book):
        large_course_name = "a" * 100
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("student1", large_course_name, 90)
        assert result == True
        assert grade_book.grades == {"student1": {large_course_name: 90}}

    def test_edge_case_register_student_with_special_characters(self, student_registry, grade_book):
        student_registry.register_student("student@123#", "Alice")
        result = student_registry.add_course_grade("student@123#", "Math", 90)
        assert result == True
        assert grade_book.grades == {"student@123#": {"Math": 90}}

    def test_edge_case_add_grade_with_special_characters(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        result = student_registry.add_course_grade("student1", "Math@123#", 90)
        assert result == True
        assert grade_book.grades == {"student1": {"Math@123#": 90}}

    def test_edge_case_add_multiple_students_and_grades(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        student_registry.register_student("student2", "Bob")
        student_registry.add_course_grade("student1", "Math", 90)
        student_registry.add_course_grade("student1", "Science", 85)
        student_registry.add_course_grade("student2", "Math", 80)
        assert grade_book.grades == {
            "student1": {"Math": 90, "Science": 85},
            "student2": {"Math": 80}
        }

    def test_edge_case_get_average_for_registered_student(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        student_registry.add_course_grade("student1", "Math", 90)
        student_registry.add_course_grade("student1", "Science", 85)
        average = grade_book.get_average("student1")
        assert average == 87.5

    def test_edge_case_get_average_for_unregistered_student(self, student_registry, grade_book):
        average = grade_book.get_average("student1")
        assert average is None

    def test_edge_case_get_average_for_student_with_no_grades(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        average = grade_book.get_average("student1")
        assert average is None

    def test_edge_case_get_average_for_student_with_one_grade(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        student_registry.add_course_grade("student1", "Math", 90)
        average = grade_book.get_average("student1")
        assert average == 90.0

    def test_edge_case_get_average_for_student_with_large_number_of_grades(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        for i in range(100):
            student_registry.add_course_grade("student1", f"Course{i}", 90)
        average = grade_book.get_average("student1")
        assert average == 90.0

    def test_edge_case_get_average_for_student_with_negative_grades(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        student_registry.add_course_grade("student1", "Math", -10)
        student_registry.add_course_grade("student1", "Science", -20)
        average = grade_book.get_average("student1")
        assert average == -15.0

    def test_edge_case_get_average_for_student_with_large_grades(self, student_registry, grade_book):
        student_registry.register_student("student1", "Alice")
        student_registry.add_course_grade("student1", "Math", 1000)
        student_registry.add_course_grade("student1", "Science", 2000)
        average = grade_book.get_average("student1")
        assert average == 1500.0