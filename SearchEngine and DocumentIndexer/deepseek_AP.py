import pytest
from unittest.mock import MagicMock
from DocumentIndexer import DocumentIndexer
from SearchEngine import SearchEngine

class TestIntegrationSearchEngine:
    def setup_method(self):
        self.mock_indexer = MagicMock(spec=DocumentIndexer)
        self.engine = SearchEngine(self.mock_indexer)

    def test_add_document_success_flow(self):
        self.mock_indexer.add_document.return_value = True
        
        result = self.engine.add_document("doc1", "integration test")
        
        assert result is True
        self.mock_indexer.add_document.assert_called_once_with("doc1", "integration test")
        assert "doc1" in self.engine.documents

    def test_search_ranking_logic(self):
        self.mock_indexer.get_documents_with_word.side_effect = [
            ["doc1", "doc2"],  # "test"
            ["doc1"]            # "case"
        ]
        
        results = self.engine.search("Test Case")
        
        assert results == ["doc1", "doc2"]
        self.mock_indexer.get_documents_with_word.assert_any_call("test")
        self.mock_indexer.get_documents_with_word.assert_any_call("case")

    def test_indexer_failure_propagation(self):
        self.mock_indexer.add_document.side_effect = RuntimeError("Indexing failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            self.engine.add_document("doc3", "error test")
        assert "Indexing failed" in str(exc_info.value)

    def test_empty_query_handling(self):
        assert self.engine.search("") == []

    def test_edge_case_duplicate_words(self):
        self.mock_indexer.get_documents_with_word.return_value = ["doc1"]
        
        results = self.engine.search("word word word")
        assert results == ["doc1"]
        assert self.mock_indexer.get_documents_with_word.call_count == 3

    def test_real_integration_flow(self):
        real_indexer = DocumentIndexer()
        engine = SearchEngine(real_indexer)
        
        engine.add_document("doc1", "rabbit hole")
        engine.add_document("doc2", "mad hatter rabbit")
        
        assert engine.search("rabbit") == ["doc1", "doc2"]
        assert engine.search("hatter") == ["doc2"]
        assert engine.search("cheshire") == []