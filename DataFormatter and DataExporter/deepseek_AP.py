import pytest
from unittest.mock import MagicMock, mock_open, patch
from DataExporter import DataExporter
from DataFormatter import DataFormatter

class TestIntegrationDataExporterFormatter:
    def setup_method(self):
        self.mock_formatter = MagicMock(spec=DataFormatter)
        self.exporter = DataExporter(self.mock_formatter)

    # Success path
    def test_export_valid_data(self):
        test_data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        self.mock_formatter.format_to_csv.return_value = "id,name\n1,Alice\n2,Bob"
        
        with patch("builtins.open", mock_open()) as mocked_file:
            result = self.exporter.export_to_file(test_data, "output.csv")
            
            self.mock_formatter.format_to_csv.assert_called_once_with(test_data)
            mocked_file().write.assert_called_once_with("id,name\n1,Alice\n2,Bob")
            assert result == 2

    # Partial failure
    def test_formatter_error_propagates(self):
        self.mock_formatter.format_to_csv.side_effect = ValueError("Invalid data format")
        
        with patch("builtins.open", mock_open()), pytest.raises(ValueError) as exc_info:
            self.exporter.export_to_file([{"invalid": "data"}], "error.csv")
            
        assert "Invalid data format" in str(exc_info.value)
        self.mock_formatter.format_to_csv.assert_called_once()

    # Edge case: empty data
    def test_export_empty_data(self):
        self.mock_formatter.format_to_csv.return_value = ""
        
        with patch("builtins.open", mock_open()) as mocked_file:
            result = self.exporter.export_to_file([], "empty.csv")
            
            self.mock_formatter.format_to_csv.assert_called_once_with([])
            mocked_file().write.assert_called_once_with("")
            assert result == 0

    # Real integration with actual formatter
    def test_real_integration_with_formatter(self, tmp_path):
        real_formatter = DataFormatter()
        exporter = DataExporter(real_formatter)
        data = [{"col1": "A", "col2": 100}, {"col1": "B", "col2": 200}]
        filename = tmp_path / "data.csv"
        
        result = exporter.export_to_file(data, filename)
        
        assert result == 2
        with open(filename, 'r') as f:
            content = f.read().strip()
        assert content == "col1,col2\nA,100\nB,200"