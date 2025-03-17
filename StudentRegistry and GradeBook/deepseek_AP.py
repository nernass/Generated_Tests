import pytest
from unittest.mock import MagicMock
from GradeBook import GradeBook
from StudentRegistry import StudentRegistry

class TestIntegrationStudentRegistry:
    def setup_method(self):
        self.mock_gradebook = MagicMock(spec=GradeBook)
        self.registry = StudentRegistry(self.mock_gradebook)

    def test_valid_grade_addition_flow(self):
        self.registry.register_student("S001", "Alice")
        self.mock_gradebook.add_grade.return_value = True
        
        assert self.registry.add_course_grade("S001", "Math", 90) is True
        self.mock_gradebook.add_grade.assert_called_once_with("S001", "Math", 90)

    def test_gradebook_failure_propagation(self):
        self.registry.register_student("S002", "Bob")
        self.mock_gradebook.add_grade.side_effect = RuntimeError("Grade storage error")
        
        with pytest.raises(RuntimeError) as exc_info:
            self.registry.add_course_grade("S002", "Physics", 85)
        assert "Grade storage error" in str(exc_info.value)

    def test_unregistered_student_handling(self):
        assert self.registry.add_course_grade("S999", "Chemistry", 75) is False
        self.mock_gradebook.add_grade.assert_not_called()

    def test_edge_case_negative_grade(self):
        self.registry.register_student("S003", "Charlie")
        self.mock_gradebook.add_grade.return_value = True
        
        assert self.registry.add_course_grade("S003", "Art", -5) is True
        self.mock_gradebook.add_grade.assert_called_once_with("S003", "Art", -5)

    def test_real_integration_end_to_end(self):
        real_gradebook = GradeBook()
        registry = StudentRegistry(real_gradebook)
        
        registry.register_student("S100", "Dave")
        registry.add_course_grade("S100", "History", 88)
        registry.add_course_grade("S100", "Biology", 92)
        
        assert real_gradebook.get_average("S100") == 90.0
        assert registry.add_course_grade("S404", "Math", 70) is False