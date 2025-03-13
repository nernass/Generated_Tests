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