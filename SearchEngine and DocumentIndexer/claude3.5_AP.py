import pytest
from unittest.mock import Mock, patch
import logging
from DocumentIndexer import DocumentIndexer
from SearchEngine import SearchEngine

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestSearchEngineIndexerIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment before each test"""
        self.indexer = DocumentIndexer()
        self.search_engine = SearchEngine(self.indexer)
        yield
        # Cleanup after each test
        self.indexer.index.clear()
        self.search_engine.documents.clear()

    def test_successful_workflow(self):
        """Test successful document addition and search workflow"""
        # Add test documents
        test_docs = {
            "doc1": "python testing integration",
            "doc2": "python programming guide",
            "doc3": "integration testing best practices"
        }
        
        for doc_id, content in test_docs.items():
            assert self.search_engine.add_document(doc_id, content)
            logger.debug(f"Added document {doc_id}: {content}")

        # Verify document storage
        assert len(self.search_engine.documents) == 3
        assert "python" in self.indexer.index
        assert set(self.indexer.index["python"]) == {"doc1", "doc2"}

        # Test search functionality
        python_results = self.search_engine.search("python")
        assert len(python_results) == 2
        assert set(python_results) == {"doc1", "doc2"}

        integration_results = self.search_engine.search("integration testing")
        assert len(integration_results) == 2
        assert integration_results[0] in ["doc1", "doc3"]

    def test_indexer_failure_handling(self):
        """Test system behavior when indexer fails"""
        with patch.object(self.indexer, 'add_document') as mock_add:
            # Simulate indexer failure
            mock_add.side_effect = Exception("Indexer failure")
            
            with pytest.raises(Exception) as exc_info:
                self.search_engine.add_document("doc1", "test content")
            
            assert str(exc_info.value) == "Indexer failure"
            assert "doc1" not in self.search_engine.documents
            logger.debug("Indexer failure handled correctly")

    def test_edge_cases(self):
        """Test system behavior with edge cases"""
        # Empty document
        assert self.search_engine.add_document("empty_doc", "")
        assert "empty_doc" in self.search_engine.documents
        assert self.search_engine.search("") == []

        # Very large document
        large_content = " ".join(["word"] * 1000)
        assert self.search_engine.add_document("large_doc", large_content)
        assert "large_doc" in self.search_engine.documents
        assert "word" in self.indexer.index
        assert "large_doc" in self.indexer.index["word"]

        # Special characters
        special_content = "Hello! @#$%^&* World"
        assert self.search_engine.add_document("special_doc", special_content)
        assert "hello" in self.indexer.index
        assert "world" in self.indexer.index

    def test_concurrent_operations(self):
        """Test system behavior with multiple operations"""
        # Add multiple documents with overlapping words
        docs = {
            f"doc{i}": f"content{i} shared_word test{i}"
            for i in range(5)
        }
        
        for doc_id, content in docs.items():
            assert self.search_engine.add_document(doc_id, content)

        # Verify word indexing
        assert "shared_word" in self.indexer.index
        assert len(self.indexer.index["shared_word"]) == 5

        # Test search with multiple matches
        results = self.search_engine.search("shared_word")
        assert len(results) == 5

    def test_data_consistency(self):
        """Test data consistency between SearchEngine and DocumentIndexer"""
        test_doc = "python integration test"
        doc_id = "test_doc"

        # Add document
        self.search_engine.add_document(doc_id, test_doc)

        # Verify consistency
        assert doc_id in self.search_engine.documents
        assert self.search_engine.documents[doc_id] == test_doc
        
        for word in test_doc.split():
            assert word.lower() in self.indexer.index
            assert doc_id in self.indexer.index[word.lower()]

        # Verify search results match indexed content
        for word in test_doc.split():
            results = self.search_engine.search(word)
            assert doc_id in results
            assert results == self.indexer.get_documents_with_word(word)