import pytest
from unittest.mock import Mock, patch
from DataFormatter import DataFormatter
from DataExporter import DataExporter

@pytest.fixture
def formatter():
    return DataFormatter()

@pytest.fixture
def exporter(formatter):
    return DataExporter(formatter)

def test_export_to_file_success(exporter):
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    filename = "output.csv"
    
    with patch("builtins.open", new_callable=Mock) as mock_open:
        result = exporter.export_to_file(data, filename)
        
        mock_open.assert_called_once_with(filename, 'w')
        mock_open().write.assert_called_once_with("name,age\nAlice,30\nBob,25")
        assert result == len(data)

def test_export_to_file_empty_data(exporter):
    data = []
    filename = "output.csv"
    
    with patch("builtins.open", new_callable=Mock) as mock_open:
        result = exporter.export_to_file(data, filename)
        
        mock_open.assert_called_once_with(filename, 'w')
        mock_open().write.assert_called_once_with("")
        assert result == len(data)

def test_export_to_file_invalid_data(exporter):
    data = None
    filename = "output.csv"
    
    with patch("builtins.open", new_callable=Mock) as mock_open:
        result = exporter.export_to_file(data, filename)
        
        mock_open.assert_called_once_with(filename, 'w')
        mock_open().write.assert_called_once_with("")
        assert result == 0