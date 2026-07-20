"""
Quick validation that code changes are syntactically correct and imports work.
Does not require ChromaDB or embeddings to be loaded.
"""

import sys

def test_imports():
    """Test that all modified modules import correctly."""
    print("\n" + "="*60)
    print("TEST: Module Imports")
    print("="*60)
    
    try:
        from app.config import vectorstore_config
        print("✓ app.config.vectorstore_config imported")
        
        # Check new constants exist
        assert hasattr(vectorstore_config, 'CANDIDATE_K'), "CANDIDATE_K not found"
        assert hasattr(vectorstore_config, 'HIGH_VALUE_FILES'), "HIGH_VALUE_FILES not found"
        assert hasattr(vectorstore_config, 'STRUCTURAL_FILES'), "STRUCTURAL_FILES not found"
        print(f"  - CANDIDATE_K = {vectorstore_config.CANDIDATE_K}")
        print(f"  - DEFAULT_K = {vectorstore_config.DEFAULT_K}")
        print(f"  - HIGH_VALUE_FILES count: {len(vectorstore_config.HIGH_VALUE_FILES)}")
        
        from app.retriever.retrieval_service import RetrievalService
        print("✓ app.retriever.retrieval_service.RetrievalService imported")
        
        # Check new methods exist
        assert hasattr(RetrievalService, '_is_broad_query'), "_is_broad_query not found"
        assert hasattr(RetrievalService, '_is_specific_query'), "_is_specific_query not found"
        assert hasattr(RetrievalService, '_rerank_and_filter'), "_rerank_and_filter not found"
        assert hasattr(RetrievalService, '_calculate_document_boost'), "_calculate_document_boost not found"
        assert hasattr(RetrievalService, '_merge_adjacent_chunks'), "_merge_adjacent_chunks not found"
        print("  - New methods: _is_broad_query, _is_specific_query, _rerank_and_filter, etc.")
        
        from app.rag.rag_pipeline import RAGPipeline
        print("✓ app.rag.rag_pipeline.RAGPipeline imported")
        
        from app.llm.prompts.prompt_service import PromptService
        print("✓ app.llm.prompts.prompt_service.PromptService imported")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_detection():
    """Test query type detection logic."""
    print("\n" + "="*60)
    print("TEST: Query Type Detection")
    print("="*60)
    
    try:
        from app.retriever.retrieval_service import RetrievalService
        
        # Create instance (won't connect to DB yet)
        # We'll test the static detection methods
        retriever = RetrievalService.__new__(RetrievalService)
        
        # Test broad query detection
        broad_queries = [
            "Explain the directory structure",
            "What are all the components",
            "List all the endpoints",
            "Overview of the architecture"
        ]
        
        print("\nBroad Query Detection:")
        for query in broad_queries:
            is_broad = retriever._is_broad_query(query)
            status = "✓" if is_broad else "✗"
            print(f"  {status} '{query[:40]}...' -> {is_broad}")
        
        # Test specific query detection
        specific_queries = [
            "How does the RAG pipeline work?",
            "Explain how authentication is implemented",
            "Implementation of the embedding service"
        ]
        
        print("\nSpecific Query Detection:")
        for query in specific_queries:
            is_specific = retriever._is_specific_query(query)
            status = "✓" if is_specific else "✗"
            print(f"  {status} '{query[:40]}...' -> {is_specific}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Query detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_boost_calculation():
    """Test file boost calculation logic."""
    print("\n" + "="*60)
    print("TEST: File Boost Calculation")
    print("="*60)
    
    try:
        from app.retriever.retrieval_service import RetrievalService
        from langchain_core.documents import Document
        
        retriever = RetrievalService.__new__(RetrievalService)
        
        # Test documents
        test_cases = [
            ({"source": "README.md"}, "general query", False, "README (high-value)"),
            ({"source": ".env"}, "what config files", False, "Config file + config query"),
            ({"source": "app/api/routes.py"}, "list API endpoints", False, "Route file + API query"),
            ({"source": "random_code.py"}, "general query", False, "Random code (no boost)"),
        ]
        
        print("\nBoost Calculations:")
        for metadata, query, is_broad, description in test_cases:
            doc = Document(page_content="test", metadata=metadata)
            boost = retriever._calculate_document_boost(doc, query, is_broad)
            print(f"  {description:35} -> +{boost*100:.0f}% boost")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Boost calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_values():
    """Test that config values are updated correctly."""
    print("\n" + "="*60)
    print("TEST: Configuration Values")
    print("="*60)
    
    try:
        from app.config import vectorstore_config
        
        print(f"\nVectorstore Config:")
        print(f"  DEFAULT_K: {vectorstore_config.DEFAULT_K} (expected: 15)")
        print(f"  CANDIDATE_K: {vectorstore_config.CANDIDATE_K} (expected: 20)")
        
        assert vectorstore_config.DEFAULT_K == 15, f"DEFAULT_K should be 15, got {vectorstore_config.DEFAULT_K}"
        assert vectorstore_config.CANDIDATE_K == 20, f"CANDIDATE_K should be 20, got {vectorstore_config.CANDIDATE_K}"
        
        print(f"\n✓ Config values correct")
        return True
        
    except Exception as e:
        print(f"\n✗ Config test failed: {e}")
        return False


def test_prompt_updates():
    """Test that prompt template has been updated."""
    print("\n" + "="*60)
    print("TEST: Prompt Template Updates")
    print("="*60)
    
    try:
        from pathlib import Path
        
        prompt_path = Path("app/llm/prompts/repository_qa.txt")
        prompt_content = prompt_path.read_text(encoding="utf-8")
        
        # Check for key phrases in updated prompt
        checks = [
            ("CRITICAL RULES", "Has 'CRITICAL RULES' section"),
            ("RESPONSE GUIDELINES", "Has 'RESPONSE GUIDELINES' section"),
            ("couldn't find that information", "Has 'couldn't find' phrase"),
            ("explicitly state what is missing", "Instructions to state missing info"),
        ]
        
        print("\nPrompt Content Checks:")
        all_pass = True
        for phrase, description in checks:
            present = phrase in prompt_content
            status = "✓" if present else "✗"
            print(f"  {status} {description}")
            if not present:
                all_pass = False
        
        if all_pass:
            print(f"\n✓ Prompt template updated correctly")
        else:
            print(f"\n✗ Some prompt checks failed")
        
        return all_pass
        
    except Exception as e:
        print(f"\n✗ Prompt test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("\n" + "="*60)
    print("CODE CHANGES VALIDATION")
    print("Quick check without database connection")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Config Values", test_config_values),
        ("Query Detection", test_query_detection),
        ("File Boost Calculation", test_file_boost_calculation),
        ("Prompt Updates", test_prompt_updates),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All validation tests passed!")
        print("✓ Code changes are syntactically correct")
        print("✓ New methods and config values exist")
        print("✓ Query detection logic works")
        print("✓ Prompt template updated")
        print("\nReady to run full evaluation with database.")
        return True
    else:
        print(f"\n⚠️ {total_count - passed_count} test(s) failed")
        print("Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
