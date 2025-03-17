import pytest
import os
from DataFormatter import DataFormatter
from DataExporter import DataExporter

@pytest.fixture
def test_data():
    return [
        {"name": "John", "age": "30", "city": "New York"},
        {"name": "Alice", "age": "25", "city": "London"}
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
    assert content.strip() == ""

def test_invalid_data_handling(exporter, tmp_path):
    # Arrange
    test_file = tmp_path / "error_output.csv"
    invalid_data = [{"name": "John"}, {"age": "30"}]  # Inconsistent keys
    
    # Act & Assert
    with pytest.raises(KeyError):
        exporter.export_to_file(invalid_data, str(test_file))