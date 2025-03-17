import pytest
from unittest.mock import MagicMock
from DocumentIndexer import DocumentIndexer
from SearchEngine import SearchEngine

class TestIntegrationSearchEngine:
    def setup_method(self):
        self.mock_indexer = MagicMock(spec=DocumentIndexer)
        self.engine = SearchEngine(self.mock_indexer)

    def test_add_document_flow(self):
        self.mock_indexer.add_document.return_value = True
        
        result = self.engine.add_document("doc1", "Hello world")
        
        assert result is True
        self.mock_indexer.add_document.assert_called_once_with("doc1", "Hello world")
        assert "doc1" in self.engine.documents

    def test_search_valid_query(self):
        self.mock_indexer.get_documents_with_word.side_effect = [
            ["doc1", "doc2"],  # hello
            ["doc1"]            # world
        ]
        
        results = self.engine.search("Hello World")
        
        assert results == ["doc1", "doc2"]
        self.mock_indexer.get_documents_with_word.assert_any_call("hello")
        self.mock_indexer.get_documents_with_word.assert_any_call("world")

    def test_search_no_results(self):
        self.mock_indexer.get_documents_with_word.return_value = []
        
        assert self.engine.search("nonexistent") == []

    def test_indexer_failure_propagation(self):
        self.mock_indexer.add_document.side_effect = Exception("Indexing error")
        
        with pytest.raises(Exception) as exc_info:
            self.engine.add_document("doc3", "Test content")
        assert "Indexing error" in str(exc_info.value)

    def test_edge_case_empty_content(self):
        self.mock_indexer.add_document.return_value = True
        
        assert self.engine.add_document("empty_doc", "") is True
        self.mock_indexer.add_document.assert_called_once_with("empty_doc", "")

    def test_real_integration_end_to_end(self):
        real_indexer = DocumentIndexer()
        engine = SearchEngine(real_indexer)
        
        engine.add_document("doc1", "apple banana")
        engine.add_document("doc2", "banana cherry")
        
        assert engine.search("banana") == ["doc1", "doc2"]
        assert engine.search("apple cherry") == ["doc1", "doc2"]  # doc1:1, doc2:1 (tie order depends on insertion)