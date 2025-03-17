import pytest
from unittest.mock import MagicMock, patch
from GradeBook import GradeBook
from StudentRegistry import StudentRegistry

class TestStudentRegistryGradeBookIntegration:
    @pytest.fixture
    def mock_grade_book(self):
        """Create a mock GradeBook for isolated StudentRegistry testing"""
        return MagicMock(spec=GradeBook)
    
    @pytest.fixture
    def real_setup(self):
        """Set up actual instances for integration testing"""
        grade_book = GradeBook()
        registry = StudentRegistry(grade_book)
        return registry, grade_book
    
    # Top-down integration tests
    def test_end_to_end_success_flow(self, real_setup):
        """Test successful interaction between StudentRegistry and GradeBook"""
        registry, grade_book = real_setup
        
        # Register student
        student_id = "12345"
        assert registry.register_student(student_id, "John Doe")
        
        # Add grades through registry (which uses grade_book)
        assert registry.add_course_grade(student_id, "Math", 90)
        assert registry.add_course_grade(student_id, "Science", 85)
        assert registry.add_course_grade(student_id, "History", 95)
        
        # Verify data flow through components
        assert student_id in registry.students
        assert registry.students[student_id]["name"] == "John Doe"
        assert student_id in grade_book.grades
        assert grade_book.grades[student_id]["Math"] == 90
        assert grade_book.grades[student_id]["Science"] == 85
        assert grade_book.grades[student_id]["History"] == 95
        
        # Verify average calculation works
        assert grade_book.get_average(student_id) == 90.0
    
    def test_error_handling_unregistered_student(self, real_setup):
        """Test error handling when adding grade for non-existent student"""
        registry, grade_book = real_setup
        
        # Attempt to add grade for unregistered student
        result = registry.add_course_grade("nonexistent", "Math", 90)
        
        # Verify error handling
        assert result is False
        assert "nonexistent" not in grade_book.grades
    
    def test_duplicate_student_registration(self, real_setup):
        """Test system handles duplicate registration attempts"""
        registry, grade_book = real_setup
        
        # Register student successfully
        student_id = "12345"
        assert registry.register_student(student_id, "John Doe")
        
        # Try registering again with same ID
        assert registry.register_student(student_id, "Jane Smith") is False
        
        # Verify original data preserved
        assert registry.students[student_id]["name"] == "John Doe"
    
    def test_grade_override(self, real_setup):
        """Test system handles grade updates correctly"""
        registry, grade_book = real_setup
        
        student_id = "12345"
        registry.register_student(student_id, "John Doe")
        
        # Add initial grade
        registry.add_course_grade(student_id, "Math", 80)
        assert grade_book.grades[student_id]["Math"] == 80
        
        # Override with new grade
        registry.add_course_grade(student_id, "Math", 95)
        assert grade_book.grades[student_id]["Math"] == 95
    
    def test_multiple_students_isolation(self, real_setup):
        """Test system correctly handles multiple students without cross-contamination"""
        registry, grade_book = real_setup
        
        # Register two students
        registry.register_student("001", "Alice")
        registry.register_student("002", "Bob")
        
        # Add grades for each
        registry.add_course_grade("001", "Math", 90)
        registry.add_course_grade("002", "Math", 85)
        
        # Verify data isolation
        assert grade_book.grades["001"]["Math"] == 90
        assert grade_book.grades["002"]["Math"] == 85
    
    def test_empty_grades_average(self, real_setup):
        """Test edge case: calculating average for student with no grades"""
        registry, grade_book = real_setup
        
        student_id = "12345"
        registry.register_student(student_id, "John Doe")
        
        # Calculate average when no grades exist
        average = grade_book.get_average(student_id)
        assert average is None
    
    # Component isolation tests with mocks
    def test_registry_uses_gradebook_correctly(self, mock_grade_book):
        """Test StudentRegistry delegates to GradeBook with correct parameters"""
        # Set up mocked GradeBook
        mock_grade_book.add_grade.return_value = True
        
        # Create registry with mock
        registry = StudentRegistry(mock_grade_book)
        
        # Register student and add grade
        registry.register_student("12345", "John Doe")
        registry.add_course_grade("12345", "Math", 90)
        
        # Verify GradeBook was called with correct parameters
        mock_grade_book.add_grade.assert_called_once_with("12345", "Math", 90)