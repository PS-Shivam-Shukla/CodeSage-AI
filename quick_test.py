"""
Quick test script to verify RAG improvements without full evaluation.
Tests a single question to check if query expansion and retrieval are working.
"""

from app.rag.rag_pipeline import RAGPipeline
from app.retriever.query_expander import QueryExpander

def test_query_expansion():
    """Test the query expansion module."""
    print("=" * 80)
    print("Testing Query Expansion")
    print("=" * 80)
    
    expander = QueryExpander()
    
    test_queries = [
        "What is the API architecture?",
        "How does authentication work?",
        "List all classes in the repository"
    ]
    
    for query in test_queries:
        print(f"\nOriginal: {query}")
        expanded = expander.expand_query(query)
        print(f"Expanded to {len(expanded)} queries:")
        for i, eq in enumerate(expanded, 1):
            print(f"  {i}. {eq}")

def test_retrieval():
    """Test retrieval with a simple question."""
    print("\n" + "=" * 80)
    print("Testing RAG Pipeline with k=10")
    print("=" * 80)
    
    pipeline = RAGPipeline()
    
    question = "What topics are covered in this repository?"
    
    print(f"\nQuestion: {question}")
    print("Retrieving with k=10...")
    
    try:
        result = pipeline.ask_with_context(
            question=question,
            k=10
        )
        
        print(f"\n✓ Retrieved {len(result.contexts)} contexts")
        print(f"✓ Retrieval latency: {result.retrieval_latency_ms:.2f}ms")
        print(f"✓ Response time: {result.response_time_ms:.2f}ms")
        print(f"\nAnswer (first 200 chars):\n{result.answer[:200]}...")
        
        print(f"\nContext samples:")
        for i, ctx in enumerate(result.contexts[:3], 1):
            print(f"\n[Context {i}] ({len(ctx)} chars)")
            print(ctx[:150] + "...")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_query_expansion()
    test_retrieval()
    print("\n" + "=" * 80)
    print("Quick test complete!")
    print("=" * 80)
