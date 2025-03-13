class DataExporter:
    def __init__(self, formatter):
        self.formatter = formatter
        
    def export_to_file(self, data, filename):
        formatted_data = self.formatter.format_to_csv(data)
        with open(filename, 'w') as f:
            f.write(formatted_data)
        return len(data)