import pytest
from unittest.mock import Mock, patch
from DocumentIndexer import DocumentIndexer
from SearchEngine import SearchEngine

@pytest.fixture
def setup_environment():
    indexer = DocumentIndexer()
    search_engine = SearchEngine(indexer)
    return search_engine, indexer

def test_success_path(setup_environment):
    search_engine, indexer = setup_environment
    
    # Add documents
    search_engine.add_document("doc1", "the quick brown fox")
    search_engine.add_document("doc2", "lazy fox jumps over")
    search_engine.add_document("doc3", "quick brown dog sleeps")
    
    # Validate end-to-end data flow
    assert search_engine.search("fox") == ["doc1", "doc2"]
    assert search_engine.search("quick") == ["doc1", "doc3"]
    assert search_engine.search("quick brown") == ["doc1", "doc3"]

def test_partial_failure(setup_environment):
    search_engine, indexer = setup_environment
    
    # Mock indexer to throw an exception
    with patch.object(indexer, 'add_document', side_effect=Exception("Indexer failure")):
        with pytest.raises(Exception, match="Indexer failure"):
            search_engine.add_document("doc1", "the quick brown fox")
    
    # Verify error handling/rollback
    assert "doc1" not in search_engine.documents

def test_edge_case_empty_input(setup_environment):
    search_engine, indexer = setup_environment
    
    # Test empty document
    assert search_engine.add_document("empty_doc", "") == True
    assert search_engine.search("") == []

def test_edge_case_large_input(setup_environment):
    search_engine, indexer = setup_environment
    
    # Test large document
    large_content = "word " * 10000
    search_engine.add_document("large_doc", large_content)
    
    # Validate large input handling
    assert search_engine.search("word") == ["large_doc"]

def test_edge_case_special_characters(setup_environment):
    search_engine, indexer = setup_environment
    
    # Test document with special characters
    search_engine.add_document("special_doc", "hello! @world #python")
    
    # Validate special characters handling
    assert search_engine.search("hello") == ["special_doc"]
    assert search_engine.search("world") == ["special_doc"]
    assert search_engine.search("python") == ["special_doc"]