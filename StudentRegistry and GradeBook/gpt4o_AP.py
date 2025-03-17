import pytest
from unittest.mock import Mock, patch
from GradeBook import GradeBook
from StudentRegistry import StudentRegistry

class TestStudentManagementIntegration:
    @pytest.fixture
    def mock_gradebook(self):
        return Mock(spec=GradeBook)

    @pytest.fixture
    def setup(self):
        gradebook = GradeBook()
        registry = StudentRegistry(gradebook)
        return registry, gradebook

    def test_successful_student_registration_and_grading(self, setup):
        registry, gradebook = setup
        student_id = "ST001"
        
        # Test student registration
        assert registry.register_student(student_id, "John Doe")
        assert student_id in registry.students
        
        # Test grade assignment
        assert registry.add_course_grade(student_id, "Math", 95)
        assert gradebook.grades[student_id]["Math"] == 95
        
        # Test grade calculation
        assert gradebook.get_average(student_id) == 95

    def test_gradebook_failure_handling(self, mock_gradebook):
        mock_gradebook.add_grade.side_effect = Exception("Database connection failed")
        registry = StudentRegistry(mock_gradebook)
        
        student_id = "ST001"
        registry.register_student(student_id, "Jane Doe")
        
        with pytest.raises(Exception):
            registry.add_course_grade(student_id, "Physics", 85)

    def test_invalid_student_registration(self, setup):
        registry, gradebook = setup
        student_id = "ST001"
        
        # Register student
        assert registry.register_student(student_id, "John Doe")
        
        # Attempt duplicate registration
        assert not registry.register_student(student_id, "Jane Doe")
        assert registry.students[student_id]["name"] == "John Doe"

    def test_multiple_course_grades(self, setup):
        registry, gradebook = setup
        student_id = "ST001"
        
        registry.register_student(student_id, "Alice Smith")
        registry.add_course_grade(student_id, "Math", 90)
        registry.add_course_grade(student_id, "Physics", 85)
        registry.add_course_grade(student_id, "Chemistry", 95)
        
        assert len(gradebook.grades[student_id]) == 3
        assert gradebook.get_average(student_id) == 90.0

    def test_grade_update(self, setup):
        registry, gradebook = setup
        student_id = "ST001"
        
        registry.register_student(student_id, "Bob Wilson")
        registry.add_course_grade(student_id, "Math", 80)
        registry.add_course_grade(student_id, "Math", 90)
        
        assert gradebook.grades[student_id]["Math"] == 90

    def test_unregistered_student_grade_addition(self, setup):
        registry, gradebook = setup
        student_id = "INVALID"
        
        assert not registry.add_course_grade(student_id, "Math", 85)
        assert student_id not in gradebook.grades

    def test_empty_student_average(self, setup):
        registry, gradebook = setup
        student_id = "ST001"
        
        registry.register_student(student_id, "New Student")
        assert gradebook.get_average(student_id) is None

    @patch('GradeBook.GradeBook')
    def test_gradebook_integration_mock(self, MockGradeBook):
        mock_gradebook = MockGradeBook()
        mock_gradebook.add_grade.return_value = True
        mock_gradebook.get_average.return_value = 85.0
        
        registry = StudentRegistry(mock_gradebook)
        student_id = "ST001"
        
        registry.register_student(student_id, "Test Student")
        registry.add_course_grade(student_id, "Math", 85)
        
        mock_gradebook.add_grade.assert_called_once_with(student_id, "Math", 85)