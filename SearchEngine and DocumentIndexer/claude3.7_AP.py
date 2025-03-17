import pytest
from unittest.mock import Mock, patch
import sys
import os

from DocumentIndexer import DocumentIndexer
from SearchEngine import SearchEngine

class TestSearchEngineAndIndexerIntegration:
    @pytest.fixture
    def setup(self):
        """Setup test environment with real components"""
        indexer = DocumentIndexer()
        search_engine = SearchEngine(indexer)
        return search_engine, indexer

    @pytest.fixture
    def mock_setup(self):
        """Setup test environment with mock indexer"""
        mock_indexer = Mock()
        search_engine = SearchEngine(mock_indexer)
        return search_engine, mock_indexer

    # Success Path Tests
    def test_successful_document_addition(self, setup):
        search_engine, indexer = setup
        
        # Execute workflow
        result = search_engine.add_document("doc1", "hello world python")
        
        # Assert output
        assert result is True
        assert "doc1" in search_engine.documents
        assert search_engine.documents["doc1"] == "hello world python"
        assert "hello" in indexer.index
        assert "world" in indexer.index
        assert "python" in indexer.index
        assert "doc1" in indexer.index["hello"]
        assert "doc1" in indexer.index["world"]
        assert "doc1" in indexer.index["python"]
    
    def test_successful_search(self, setup):
        search_engine, indexer = setup
        
        # Setup test data
        search_engine.add_document("doc1", "hello world")
        search_engine.add_document("doc2", "world python")
        search_engine.add_document("doc3", "hello python world")
        
        # Execute search workflow
        result1 = search_engine.search("world")
        result2 = search_engine.search("hello python")
        
        # Assert results
        assert set(result1) == {"doc1", "doc2", "doc3"}
        assert set(result2) == {"doc1", "doc3"}
        
        # Doc3 should be ranked higher for "hello python" as it contains both words
        assert result2[0] == "doc3"
    
    def test_data_flow_between_components(self, mock_setup):
        search_engine, mock_indexer = mock_setup
        
        # Configure mock
        mock_indexer.add_document.return_value = True
        
        # Execute workflow
        search_engine.add_document("doc1", "test content")
        
        # Verify correct data passed to indexer
        mock_indexer.add_document.assert_called_once_with("doc1", "test content")

    # Failure Path Tests
    def test_indexer_failure_handling(self, mock_setup):
        search_engine, mock_indexer = mock_setup
        
        # Configure mock to simulate failure
        mock_indexer.add_document.side_effect = Exception("Simulated indexer failure")
        
        # Execute workflow with error
        with pytest.raises(Exception, match="Simulated indexer failure"):
            search_engine.add_document("doc1", "test content")
        
        # Verify document was not added to search engine despite failure in indexer
        assert "doc1" not in search_engine.documents
    
    def test_search_with_failed_indexer(self, mock_setup):
        search_engine, mock_indexer = mock_setup
        
        # Configure mock for search failure
        mock_indexer.get_documents_with_word.side_effect = Exception("Indexer search failure")
        
        # Verify exception is propagated
        with pytest.raises(Exception, match="Indexer search failure"):
            search_engine.search("test")

    # Edge Case Tests
    def test_empty_inputs(self, setup):
        search_engine, indexer = setup
        
        # Test empty document
        result = search_engine.add_document("empty_doc", "")
        assert result is True
        assert "empty_doc" in search_engine.documents
        assert search_engine.documents["empty_doc"] == ""
        
        # Test empty search query
        search_result = search_engine.search("")
        assert search_result == []
    
    def test_duplicate_document_id(self, setup):
        search_engine, indexer = setup
        
        # Add document with ID "doc1" twice
        search_engine.add_document("doc1", "first version")
        search_engine.add_document("doc1", "second version")
        
        # Verify the second version overwrites the first
        assert search_engine.documents["doc1"] == "second version"
        
        # Verify search works correctly
        assert "doc1" in search_engine.search("second")
        assert "doc1" not in search_engine.search("first")
    
    def test_special_characters_and_case_sensitivity(self, setup):
        search_engine, indexer = setup
        
        # Add document with special characters and mixed case
        search_engine.add_document("doc1", "Hello! @World# TEST")
        
        # Verify case-insensitive search
        assert "doc1" in search_engine.search("hello")
        assert "doc1" in search_engine.search("WORLD")
        assert "doc1" in search_engine.search("test")
        
        # Verify special characters are handled
        assert set(indexer.index.keys()) == {"hello", "world", "test"}
    
    def test_large_document(self, setup):
        search_engine, indexer = setup
        
        # Create large document with repeated words
        large_text = " ".join(["word"] * 1000 + ["unique"])
        
        # Add large document
        search_engine.add_document("large_doc", large_text)
        
        # Verify indexing works correctly
        assert "large_doc" in indexer.index["word"]
        assert "large_doc" in indexer.index["unique"]
        
        # Verify search works correctly
        assert "large_doc" in search_engine.search("unique")
    
    def test_many_documents_same_word(self, setup):
        search_engine, indexer = setup
        
        # Add multiple documents with the same word
        for i in range(100):
            search_engine.add_document(f"doc{i}", f"common word {i}")
        
        # Verify all documents are indexed correctly
        assert len(indexer.index["common"]) == 100
        assert len(indexer.index["word"]) == 100
        
        # Verify search returns all relevant documents
        results = search_engine.search("common")
        assert len(results) == 100