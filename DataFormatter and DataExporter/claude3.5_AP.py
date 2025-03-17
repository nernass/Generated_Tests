import pytest
from unittest.mock import Mock, patch
import os
from DataFormatter import DataFormatter
from DataExporter import DataExporter

class TestDataFormatterExporterIntegration:
    @pytest.fixture
    def test_data(self):
        return [
            {"name": "John Doe", "age": 30, "city": "New York"},
            {"name": "Jane Smith", "age": 25, "city": "London"}
        ]

    @pytest.fixture
    def formatter(self):
        return DataFormatter()

    @pytest.fixture
    def exporter(self, formatter):
        return DataExporter(formatter)

    def test_successful_export_integration(self, exporter, test_data):
        """Test successful end-to-end export flow"""
        filename = "test_output.csv"
        expected_content = "name,age,city\nJohn Doe,30,New York\nJane Smith,25,London"

        with patch("builtins.open", new_callable=Mock) as mock_file:
            # Test the integration
            result = exporter.export_to_file(test_data, filename)
            
            # Verify the interaction between components
            mock_file.assert_called_once_with(filename, 'w')
            mock_file().write.assert_called_once_with(expected_content)
            assert result == len(test_data)

    def test_formatter_failure_handling(self, exporter, test_data):
        """Test handling of formatter failures"""
        filename = "test_output.csv"
        
        # Mock the formatter to raise an exception
        mock_formatter = Mock()
        mock_formatter.format_to_csv.side_effect = Exception("Formatting failed")
        exporter.formatter = mock_formatter

        with pytest.raises(Exception) as exc_info:
            with patch("builtins.open", new_callable=Mock) as mock_file:
                exporter.export_to_file(test_data, filename)
                
        assert str(exc_info.value) == "Formatting failed"
        assert not mock_file.called

    def test_empty_data_handling(self, exporter):
        """Test handling of empty input data"""
        filename = "test_output.csv"
        empty_data = []

        with patch("builtins.open", new_callable=Mock) as mock_file:
            result = exporter.export_to_file(empty_data, filename)
            
            mock_file.assert_called_once_with(filename, 'w')
            mock_file().write.assert_called_once_with("")
            assert result == 0

    def test_large_dataset_handling(self, exporter):
        """Test handling of large datasets"""
        filename = "test_output.csv"
        large_data = [{"id": i, "value": f"test{i}"} for i in range(1000)]

        with patch("builtins.open", new_callable=Mock) as mock_file:
            result = exporter.export_to_file(large_data, filename)
            
            mock_file.assert_called_once_with(filename, 'w')
            assert mock_file().write.called
            assert result == 1000

    def test_invalid_input_handling(self, exporter):
        """Test handling of invalid input"""
        filename = "test_output.csv"
        invalid_data = None

        with patch("builtins.open", new_callable=Mock) as mock_file:
            result = exporter.export_to_file(invalid_data, filename)
            
            mock_file.assert_called_once_with(filename, 'w')
            mock_file().write.assert_called_once_with("")
            assert result == 0

    def test_file_write_failure(self, exporter, test_data):
        """Test handling of file write failures"""
        filename = "test_output.csv"

        with patch("builtins.open", new_callable=Mock) as mock_file:
            mock_file().write.side_effect = IOError("Write failed")
            
            with pytest.raises(IOError) as exc_info:
                exporter.export_to_file(test_data, filename)
                
            assert str(exc_info.value) == "Write failed"