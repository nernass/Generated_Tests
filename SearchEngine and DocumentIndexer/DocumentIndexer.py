class DocumentIndexer:
    def __init__(self):
        self.index = {}
        
    def add_document(self, doc_id, content):
        words = content.lower().split()
        for word in words:
            if word not in self.index:
                self.index[word] = []
            if doc_id not in self.index[word]:
                self.index[word].append(doc_id)
        return True
        
    def get_documents_with_word(self, word):
        return self.index.get(word.lower(), [])
