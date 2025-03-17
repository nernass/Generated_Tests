import pytest
from DocumentIndexer import DocumentIndexer
from SearchEngine import SearchEngine

def test_search_engine_with_indexer_integration():
    # Setup
    indexer = DocumentIndexer()
    search_engine = SearchEngine(indexer)
    
    # Test document addition and retrieval
    doc1 = "the quick brown fox"
    doc2 = "lazy fox jumps over"
    doc3 = "quick brown dog sleeps"
    
    search_engine.add_document("doc1", doc1)
    search_engine.add_document("doc2", doc2)
    search_engine.add_document("doc3", doc3)
    
    # Test single word search
    assert search_engine.search("fox") == ["doc1", "doc2"]
    assert search_engine.search("quick") == ["doc1", "doc3"]
    
    # Test multiple word search
    assert search_engine.search("quick brown") == ["doc1", "doc3"]
    
    # Test case insensitivity
    assert search_engine.search("FOX") == ["doc1", "doc2"]
    
    # Test non-existent word
    assert search_engine.search("elephant") == []
    
    # Test empty search
    assert search_engine.search("") == []
    
    # Test document frequency ranking
    search_engine.add_document("doc4", "brown fox brown")
    results = search_engine.search("brown")
    assert results[0] == "doc4"  # Should be first due to higher frequency

def test_error_handling():
    indexer = DocumentIndexer()
    search_engine = SearchEngine(indexer)
    
    # Test with None values
    with pytest.raises(AttributeError):
        search_engine.add_document("doc1", None)
    
    with pytest.raises(AttributeError):
        search_engine.add_document(None, "test content")
    
    # Test with empty document
    assert search_engine.add_document("doc1", "") == True
    assert search_engine.search("") == []

def test_document_persistence():
    indexer = DocumentIndexer()
    search_engine = SearchEngine(indexer)
    
    # Add documents
    search_engine.add_document("doc1", "test document one")
    search_engine.add_document("doc2", "test document two")
    
    # Verify documents are stored in both engine and indexer
    assert "doc1" in search_engine.documents
    assert "test" in indexer.index
    assert "doc1" in indexer.index["test"]
    assert "doc2" in indexer.index["test"]