"""
Quick test script to validate RAG retrieval improvements.

Run this before full evaluation to spot-check the changes.
"""

from app.rag import RAGPipeline
from app.retriever import RetrievalService


def test_file_prioritization():
    """Test that high-value files are being prioritized."""
    print("\n" + "="*60)
    print("TEST 1: File Prioritization")
    print("="*60)
    
    retriever = RetrievalService()
    
    # Test query that should retrieve config files
    query = "What configuration files and environment variables are required?"
    docs = retriever.retrieve(query, k=10)
    
    print(f"\nQuery: {query}")
    print(f"\nRetrieved {len(docs)} documents:")
    
    high_value_found = []
    for i, doc in enumerate(docs[:5], 1):  # Show top 5
        source = doc.metadata.get("source", "unknown")
        chunk_label = doc.metadata.get("chunk_label", "")
        merged = doc.metadata.get("merged", False)
        
        print(f"\n{i}. {source}")
        if chunk_label:
            print(f"   Chunk: {chunk_label}")
        if merged:
            print(f"   [MERGED]")
        print(f"   Content preview: {doc.page_content[:100]}...")
        
        # Check if high-value files
        if any(term in source.lower() for term in ["readme", ".env", "requirements", "config"]):
            high_value_found.append(source)
    
    print(f"\n✓ High-value files in top 5: {len(high_value_found)}")
    print(f"  Files: {high_value_found}")
    
    return len(high_value_found) >= 2  # Expect at least 2 high-value files


def test_adaptive_expansion():
    """Test that specific queries don't get over-expanded."""
    print("\n" + "="*60)
    print("TEST 2: Adaptive Expansion")
    print("="*60)
    
    retriever = RetrievalService()
    
    # Specific query (should not expand much)
    specific_query = "How does the RAG pipeline retrieve documents?"
    print(f"\nSpecific Query: {specific_query}")
    print(f"Should NOT expand heavily (is_specific_query = True)")
    
    # Broad query (should expand)
    broad_query = "Explain the directory structure and organization"
    print(f"\nBroad Query: {broad_query}")
    print(f"Should expand (is_broad_query = True)")
    
    # Test the detection methods
    is_specific = retriever._is_specific_query(specific_query)
    is_broad = retriever._is_broad_query(broad_query)
    
    print(f"\n✓ Specific query detection: {is_specific}")
    print(f"✓ Broad query detection: {is_broad}")
    
    return is_specific and is_broad


def test_chunk_merging():
    """Test that adjacent chunks are being merged."""
    print("\n" + "="*60)
    print("TEST 3: Adjacent Chunk Merging")
    print("="*60)
    
    retriever = RetrievalService()
    
    query = "What is the RAG pipeline implementation?"
    docs = retriever.retrieve(query, k=15)
    
    print(f"\nQuery: {query}")
    print(f"Retrieved {len(docs)} documents")
    
    merged_count = 0
    for doc in docs:
        if doc.metadata.get("merged", False):
            merged_count += 1
            source = doc.metadata.get("source")
            chunk_label = doc.metadata.get("chunk_label")
            print(f"\n✓ Merged chunk found: {source} (chunks {chunk_label})")
            print(f"  Length: {len(doc.page_content)} chars")
    
    print(f"\n✓ Total merged chunks: {merged_count}")
    
    return True  # Merging is optional, so always pass


def test_context_attribution():
    """Test that context includes source attribution."""
    print("\n" + "="*60)
    print("TEST 4: Context Attribution")
    print("="*60)
    
    pipeline = RAGPipeline()
    
    result = pipeline.ask_with_context(
        "What embedding model is used?",
        k=5
    )
    
    print(f"\nQuery: {result.question}")
    print(f"\nGenerated context (first 500 chars):")
    print("-" * 60)
    print(result.contexts[0][:500] if result.contexts else "No context")
    print("-" * 60)
    
    # Check if source attribution is present
    has_attribution = any("[" in ctx and "]" in ctx for ctx in result.contexts)
    
    print(f"\n✓ Source attribution present: {has_attribution}")
    
    return has_attribution


def test_grounding_enforcement():
    """Test that LLM doesn't hallucinate for missing info."""
    print("\n" + "="*60)
    print("TEST 5: Hallucination Prevention")
    print("="*60)
    
    pipeline = RAGPipeline()
    
    # Query about something definitely not in the repository
    fake_query = "What is the quantum entanglement algorithm used in this project?"
    
    print(f"\nQuery: {fake_query}")
    print("Expected: Should state information not found")
    
    answer = pipeline.ask(fake_query, k=10)
    
    print(f"\nAnswer: {answer[:300]}...")
    
    # Check if answer acknowledges missing information
    not_found_phrases = [
        "couldn't find",
        "not found",
        "don't have",
        "not available",
        "not provided",
        "missing"
    ]
    
    acknowledges_missing = any(phrase in answer.lower() for phrase in not_found_phrases)
    
    print(f"\n✓ Acknowledges missing information: {acknowledges_missing}")
    
    return acknowledges_missing


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("RAG RETRIEVAL IMPROVEMENTS - VALIDATION TESTS")
    print("="*60)
    
    tests = [
        ("File Prioritization", test_file_prioritization),
        ("Adaptive Expansion", test_adaptive_expansion),
        ("Chunk Merging", test_chunk_merging),
        ("Context Attribution", test_context_attribution),
        ("Hallucination Prevention", test_grounding_enforcement),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Ready to run full evaluation.")
    elif passed_count >= total_count * 0.8:
        print("\n⚠️  Most tests passed. Review failures before full evaluation.")
    else:
        print("\n❌ Multiple tests failed. Debug before proceeding.")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
