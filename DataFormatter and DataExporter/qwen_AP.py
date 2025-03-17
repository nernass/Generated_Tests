import pytest
from unittest.mock import mock_open, patch, MagicMock

# Placeholder imports for the classes
# from your_module import DataExporter, DataFormatter

class DataExporter:
    def __init__(self, formatter):
        self.formatter = formatter
        
    def export_to_file(self, data, filename):
        formatted_data = self.formatter.format_to_csv(data)
        with open(filename, 'w') as f:
            f.write(formatted_data)
        return len(data)

class DataFormatter:
    def format_to_csv(self, data):
        if not data:
            return ""
            
        header = ",".join(data[0].keys())
        rows = [header]
        
        for item in data:
            row = ",".join(str(value) for value in item.values())
            rows.append(row)
            
        return "\n".join(rows)

@pytest.fixture
def data_formatter():
    return DataFormatter()

@pytest.fixture
def data_exporter(data_formatter):
    return DataExporter(data_formatter)

class TestDataExporterIntegration:

    def test_success_path_with_valid_data(self, data_exporter):
        data = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
        filename = 'test_output.csv'
        
        with patch('builtins.open', mock_open()) as mocked_file:
            result = data_exporter.export_to_file(data, filename)
            mocked_file.assert_called_once_with(filename, 'w')
            handle = mocked_file()
            handle.write.assert_called_once_with('name,age\nAlice,30\nBob,25\n')
            assert result == 2

    def test_partial_failure_with_formatter_exception(self, data_exporter):
        data = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
        filename = 'test_output.csv'
        
        # Mocking formatter to raise an exception
        data_exporter.formatter.format_to_csv = MagicMock(side_effect=Exception("Formatting failed"))
        
        with patch('builtins.open', mock_open()) as mocked_file:
            with pytest.raises(Exception) as excinfo:
                data_exporter.export_to_file(data, filename)
            assert str(excinfo.value) == "Formatting failed"
            mocked_file.assert_not_called()

    def test_edge_case_with_empty_data(self, data_exporter):
        data = []
        filename = 'test_output.csv'
        
        with patch('builtins.open', mock_open()) as mocked_file:
            result = data_exporter.export_to_file(data, filename)
            mocked_file.assert_called_once_with(filename, 'w')
            handle = mocked_file()
            handle.write.assert_called_once_with('')
            assert result == 0