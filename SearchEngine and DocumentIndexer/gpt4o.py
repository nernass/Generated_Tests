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

def test_document_ranking():
    indexer = DocumentIndexer()
    search_engine = SearchEngine(indexer)
    
    # Add documents with varying frequencies of words
    search_engine.add_document("doc1", "apple banana")
    search_engine.add_document("doc2", "apple banana apple")
    search_engine.add_document("doc3", "banana")
    
    # Test ranking by frequency
    results = search_engine.search("apple")
    assert results == ["doc2", "doc1"]
    
    results = search_engine.search("banana")
    assert results == ["doc2", "doc1", "doc3"]
    
    # Test ranking with multiple search terms
    results = search_engine.search("apple banana")
    assert results == ["doc2", "doc1", "doc3"]

def test_error_handling():
    indexer = DocumentIndexer()
    search_engine = SearchEngine(indexer)
    
    # Test with empty document
    assert search_engine.add_document("empty_doc", "") == True
    assert search_engine.search("empty") == []
    
    # Test with same document ID
    search_engine.add_document("duplicate", "first content")
    search_engine.add_document("duplicate", "second content")
    
    # The second document should overwrite the first
    assert search_engine.documents["duplicate"] == "second content"
    assert "second" in indexer.index
    assert "duplicate" in indexer.index["second"]

def test_document_indexer_interaction():
    indexer = DocumentIndexer()
    search_engine = SearchEngine(indexer)
    
    # Add documents and verify they're correctly indexed
    search_engine.add_document("doc1", "python testing")
    
    # Check if words are properly indexed
    assert "python" in indexer.index
    assert "testing" in indexer.index
    assert "doc1" in indexer.index["python"]
    assert "doc1" in indexer.index["testing"]
    
    # Verify search uses indexer correctly
    docs_with_python = indexer.get_documents_with_word("python")
    assert "doc1" in docs_with_python
    
    search_results = search_engine.search("python")
    assert search_results == docs_with_python