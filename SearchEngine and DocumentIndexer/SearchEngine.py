class SearchEngine:
    def __init__(self, indexer):
        self.indexer = indexer
        self.documents = {}
        
    def add_document(self, doc_id, content):
        self.documents[doc_id] = content
        self.indexer.add_document(doc_id, content)
        return True
        
    def search(self, query):
        results = {}
        words = query.lower().split()
        for word in words:
            doc_ids = self.indexer.get_documents_with_word(word)
            for doc_id in doc_ids:
                if doc_id not in results:
                    results[doc_id] = 0
                results[doc_id] += 1
        return sorted(results.keys(), key=lambda k: results[k], reverse=True)