import pytest
from unittest.mock import MagicMock

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

@pytest.fixture
def document_indexer():
    return DocumentIndexer()

@pytest.fixture
def search_engine(document_indexer):
    return SearchEngine(document_indexer)

class TestIntegrationDocumentIndexerAndSearchEngine:

    def test_success_path_add_document_and_search(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "The quick brown fox jumps over the lazy dog")
        search_engine.add_document("doc2", "The quick brown fox is quick")
        search_engine.add_document("doc3", "Lazy dogs are not quick")
        
        results = search_engine.search("quick brown fox")
        assert results == ["doc1", "doc2"]
        
        results = search_engine.search("lazy")
        assert results == ["doc1", "doc3"]
        
        results = search_engine.search("quick")
        assert results == ["doc1", "doc2", "doc3"]

    def test_partial_failure_indexer_add_document_fails(self, search_engine, document_indexer):
        document_indexer.add_document = MagicMock(return_value=False)
        result = search_engine.add_document("doc1", "The quick brown fox")
        assert result == False
        assert search_engine.documents == {}

    def test_partial_failure_indexer_get_documents_with_word_fails(self, search_engine, document_indexer):
        document_indexer.get_documents_with_word = MagicMock(return_value=None)
        search_engine.add_document("doc1", "The quick brown fox")
        results = search_engine.search("quick")
        assert results == []

    def test_edge_case_empty_document_content(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "")
        results = search_engine.search("quick")
        assert results == []

    def test_edge_case_empty_query(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "The quick brown fox")
        results = search_engine.search("")
        assert results == []

    def test_edge_case_special_characters_in_content(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "Hello, world!")
        results = search_engine.search("hello")
        assert results == ["doc1"]

    def test_edge_case_special_characters_in_query(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "Hello world")
        results = search_engine.search("hello!")
        assert results == ["doc1"]

    def test_edge_case_large_document_content(self, search_engine, document_indexer):
        large_content = " ".join(["word"] * 1000)
        search_engine.add_document("doc1", large_content)
        results = search_engine.search("word")
        assert results == ["doc1"]

    def test_edge_case_large_query(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "The quick brown fox")
        large_query = " ".join(["quick"] * 1000)
        results = search_engine.search(large_query)
        assert results == ["doc1"]

    def test_edge_case_duplicate_words_in_query(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "The quick brown fox")
        results = search_engine.search("quick quick quick")
        assert results == ["doc1"]

    def test_edge_case_case_insensitivity(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "The Quick Brown Fox")
        results = search_engine.search("quick brown fox")
        assert results == ["doc1"]

    def test_edge_case_multiple_documents_with_same_content(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "The quick brown fox")
        search_engine.add_document("doc2", "The quick brown fox")
        results = search_engine.search("quick brown fox")
        assert results == ["doc1", "doc2"]

    def test_edge_case_no_matching_documents(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "The quick brown fox")
        results = search_engine.search("lazy dog")
        assert results == []

    def test_edge_case_large_number_of_documents(self, search_engine, document_indexer):
        for i in range(100):
            search_engine.add_document(f"doc{i}", f"The quick brown fox {i}")
        results = search_engine.search("quick brown fox")
        assert len(results) == 100

    def test_edge_case_invalid_doc_id(self, search_engine, document_indexer):
        search_engine.add_document(None, "The quick brown fox")
        results = search_engine.search("quick")
        assert results == []

    def test_edge_case_invalid_content(self, search_engine, document_indexer):
        search_engine.add_document("doc1", None)
        results = search_engine.search("quick")
        assert results == []

    def test_edge_case_invalid_query(self, search_engine, document_indexer):
        search_engine.add_document("doc1", "The quick brown fox")
        results = search_engine.search(None)
        assert results == []

    def test_edge_case_indexer_add_document_raises_exception(self, search_engine, document_indexer):
        document_indexer.add_document = MagicMock(side_effect=Exception("Indexer error"))
        with pytest.raises(Exception) as excinfo:
            search_engine.add_document("doc1", "The quick brown fox")
        assert str(excinfo.value) == "Indexer error"
        assert search_engine.documents == {}

    def test_edge_case_indexer_get_documents_with_word_raises_exception(self, search_engine, document_indexer):
        document_indexer.get_documents_with_word = MagicMock(side_effect=Exception("Indexer error"))
        search_engine.add_document("doc1", "The quick brown fox")
        with pytest.raises(Exception) as excinfo:
            search_engine.search("quick")
        assert str(excinfo.value) == "Indexer error"