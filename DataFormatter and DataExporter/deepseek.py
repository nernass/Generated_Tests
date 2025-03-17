import pytest
from unittest.mock import MagicMock, mock_open, patch
from DataExporter import DataExporter
from DataFormatter import DataFormatter

class TestDataExporterIntegration:
    def setup_method(self):
        self.mock_formatter = MagicMock(spec=DataFormatter)
        self.exporter = DataExporter(self.mock_formatter)

    def test_valid_data_flow(self):
        test_data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        self.mock_formatter.format_to_csv.return_value = "id,name\n1,Alice\n2,Bob"
        
        with patch("builtins.open", mock_open()) as mocked_file:
            result = self.exporter.export_to_file(test_data, "test.csv")
            
            self.mock_formatter.format_to_csv.assert_called_once_with(test_data)
            mocked_file().write.assert_called_once_with("id,name\n1,Alice\n2,Bob")
            assert result == 2

    def test_formatter_failure_propagation(self):
        self.mock_formatter.format_to_csv.side_effect = ValueError("Invalid format")
        with pytest.raises(ValueError) as exc_info:
            self.exporter.export_to_file([{"broken": "data"}], "error.csv")
        assert "Invalid format" in str(exc_info.value)

    def test_empty_data_handling(self):
        self.mock_formatter.format_to_csv.return_value = ""
        with patch("builtins.open", mock_open()) as mocked_file:
            result = self.exporter.export_to_file([], "empty.csv")
            self.mock_formatter.format_to_csv.assert_called_once_with([])
            mocked_file().write.assert_called_once_with("")
            assert result == 0

    def test_real_integration_with_file_write(self, tmp_path):
        real_formatter = DataFormatter()
        exporter = DataExporter(real_formatter)
        data = [{"key": "A", "value": 100}, {"key": "B", "value": 200}]
        test_file = tmp_path / "data.csv"
        
        result = exporter.export_to_file(data, test_file)
        
        assert result == 2
        with open(test_file, 'r') as f:
            assert f.read().strip() == "key,value\nA,100\nB,200"

    def test_mixed_data_types_conversion(self):
        self.mock_formatter.format_to_csv.return_value = "field\nTrue\n3.14"
        with patch("builtins.open", mock_open()):
            result = self.exporter.export_to_file(
                [{"field": True}, {"field": 3.14}], "types.csv"
            )
            assert result == 2