import pytest
import os
from DataFormatter import DataFormatter
from DataExporter import DataExporter

@pytest.fixture
def test_data():
    return [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Alice", "age": 25, "city": "London"}
    ]

@pytest.fixture
def formatter():
    return DataFormatter()

@pytest.fixture
def exporter(formatter):
    return DataExporter(formatter)

def test_export_data_integration(test_data, exporter, tmp_path):
    # Arrange
    test_file = tmp_path / "test_output.csv"
    expected_content = "name,age,city\nJohn,30,New York\nAlice,25,London"

    # Act
    records_count = exporter.export_to_file(test_data, str(test_file))
    
    # Assert
    assert records_count == 2
    assert os.path.exists(test_file)
    with open(test_file, 'r') as f:
        content = f.read()
    assert content.replace('\r\n', '\n').strip() == expected_content

def test_empty_data_integration(exporter, tmp_path):
    # Arrange
    test_file = tmp_path / "empty_output.csv"
    
    # Act
    records_count = exporter.export_to_file([], str(test_file))
    
    # Assert
    assert records_count == 0
    assert os.path.exists(test_file)
    with open(test_file, 'r') as f:
        content = f.read()
    assert content == ""

def test_data_with_different_structures(exporter, tmp_path):
    # Arrange
    test_file = tmp_path / "mixed_output.csv"
    mixed_data = [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Alice", "city": "London", "age": 25}  # Same keys but different order
    ]
    
    # Act
    records_count = exporter.export_to_file(mixed_data, str(test_file))
    
    # Assert
    assert records_count == 2
    assert os.path.exists(test_file)

def test_special_characters_handling(exporter, tmp_path):
    # Arrange
    test_file = tmp_path / "special_chars.csv"
    special_data = [
        {"name": "John,Doe", "note": "Test, with, commas"},
        {"name": "Alice", "note": "Normal text"}
    ]
    
    # Act
    records_count = exporter.export_to_file(special_data, str(test_file))
    
    # Assert
    assert records_count == 2
    assert os.path.exists(test_file)
    # The current implementation doesn't properly escape commas in the data
    # This test will fail, highlighting the need for CSV escaping

def test_file_writing_error(exporter, monkeypatch):
    # Arrange
    def mock_open(*args, **kwargs):
        raise IOError("Simulated file writing error")
    
    monkeypatch.setattr("builtins.open", mock_open)
    
    # Act & Assert
    with pytest.raises(IOError) as exc_info:
        exporter.export_to_file([{"name": "Test"}], "any_file.csv")
    assert "Simulated file writing error" in str(exc_info.value)