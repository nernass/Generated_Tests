import pytest
from unittest.mock import MagicMock
from GradeBook import GradeBook
from StudentRegistry import StudentRegistry

class TestIntegrationStudentRegistry:
    def setup_method(self):
        self.mock_gradebook = MagicMock(spec=GradeBook)
        self.registry = StudentRegistry(self.mock_gradebook)

    def test_successful_grade_addition(self):
        self.registry.register_student("S123", "Alice")
        self.mock_gradebook.add_grade.return_value = True
        
        assert self.registry.add_course_grade("S123", "Math", 90) is True
        self.mock_gradebook.add_grade.assert_called_once_with("S123", "Math", 90)

    def test_unregistered_student_handling(self):
        self.mock_gradebook.add_grade.return_value = False
        
        assert self.registry.add_course_grade("S999", "Physics", 85) is False
        self.mock_gradebook.add_grade.assert_not_called()

    def test_gradebook_failure_propagation(self):
        self.registry.register_student("S456", "Bob")
        self.mock_gradebook.add_grade.side_effect = RuntimeError("Grade storage failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            self.registry.add_course_grade("S456", "Chemistry", 75)
        assert "Grade storage failed" in str(exc_info.value)

    def test_edge_case_duplicate_grades(self):
        self.registry.register_student("S789", "Charlie")
        self.mock_gradebook.add_grade.return_value = True
        
        self.registry.add_course_grade("S789", "Biology", 88)
        self.registry.add_course_grade("S789", "Biology", 92)
        assert self.mock_gradebook.add_grade.call_count == 2

    def test_real_integration_flow(self):
        real_gradebook = GradeBook()
        registry = StudentRegistry(real_gradebook)
        
        registry.register_student("S101", "Dave")
        registry.add_course_grade("S101", "History", 85)
        registry.add_course_grade("S101", "Art", 92)
        
        assert real_gradebook.get_average("S101") == 88.5
        assert registry.add_course_grade("S999", "Math", 70) is False