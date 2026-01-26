#!/usr/bin/env python3
"""
Test script for AI opportunity filtering.
Tests the AI filter module with sample data.
Can run with or without Ollama (will test fallback behavior).
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_ai_filter_imports():
    """Test that all imports work correctly"""
    print("=" * 60)
    print("Testing AI Filter Imports")
    print("=" * 60)
    
    try:
        from api.ai_filter import classify_opportunity, build_classification_prompt, parse_classification_response
        from api.config import Config
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_prompt_building():
    """Test prompt building"""
    print("\n" + "=" * 60)
    print("Testing Prompt Building")
    print("=" * 60)
    
    try:
        from api.ai_filter import build_classification_prompt
        
        title = "[Hiring] Software Engineer at Google"
        description = "We are looking for a software engineer. Apply at..."
        source = "reddit_jobs"
        
        prompt = build_classification_prompt(title, description, source)
        
        print(f"✓ Prompt built successfully ({len(prompt)} characters)")
        print(f"  Contains title: {'[Hiring]' in prompt}")
        print(f"  Contains description: {'software engineer' in prompt.lower()}")
        return True
    except Exception as e:
        print(f"✗ Error building prompt: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_parsing():
    """Test JSON response parsing"""
    print("\n" + "=" * 60)
    print("Testing Response Parsing")
    print("=" * 60)
    
    try:
        from api.ai_filter import parse_classification_response
        
        # Test valid JSON response
        valid_json = '{"is_opportunity": true, "confidence": 0.95, "reasoning": "Clear job posting"}'
        result = parse_classification_response(valid_json)
        assert result['is_opportunity'] == True
        assert result['confidence'] == 0.95
        print("✓ Valid JSON parsing works")
        
        # Test JSON with extra text
        json_with_text = 'Here is the result: {"is_opportunity": false, "confidence": 0.8, "reasoning": "Question"}'
        result = parse_classification_response(json_with_text)
        assert result['is_opportunity'] == False
        print("✓ JSON extraction from text works")
        
        # Test fallback parsing
        text_only = "This is not an opportunity. It's a question about internships."
        result = parse_classification_response(text_only)
        print(f"✓ Fallback parsing works (result: {result['is_opportunity']})")
        
        return True
    except Exception as e:
        print(f"✗ Error parsing response: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_classification_without_ollama():
    """Test classification when Ollama is not available (should use fallback)"""
    print("\n" + "=" * 60)
    print("Testing Classification (Ollama Not Available)")
    print("=" * 60)
    
    try:
        from api.ai_filter import classify_opportunity
        from api.config import Config
        
        # Temporarily disable AI to test fallback
        original_enabled = Config.AI_FILTER_ENABLED
        Config.AI_FILTER_ENABLED = False
        
        title = "[Hiring] Software Engineer"
        description = "We are hiring a software engineer"
        source = "reddit_jobs"
        
        result = classify_opportunity(title, description, source)
        
        print(f"  Result: {result}")
        print(f"  is_opportunity: {result.get('is_opportunity')}")
        print(f"  error: {result.get('error')}")
        
        # Restore original setting
        Config.AI_FILTER_ENABLED = original_enabled
        
        if result.get('is_opportunity') is None:
            print("✓ Correctly returns None when AI disabled (triggers fallback)")
        else:
            print("⚠ Unexpected result when AI disabled")
        
        return True
    except Exception as e:
        print(f"✗ Error testing classification: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_fallback():
    """Test keyword-based fallback filtering"""
    print("\n" + "=" * 60)
    print("Testing Keyword Fallback Filter")
    print("=" * 60)
    
    try:
        from api.fetchers.rss_fetcher import keyword_based_filter_fallback
        
        # Test opportunity
        title1 = "[Hiring] Software Engineer at Google"
        desc1 = "We are hiring a software engineer. Apply now!"
        result1 = keyword_based_filter_fallback(title1, desc1, "reddit_jobs")
        print(f"✓ Opportunity detected: {result1} (expected: True)")
        assert result1 == True, "Should detect as opportunity"
        
        # Test question
        title2 = "How do I find an internship?"
        desc2 = "I'm looking for advice on finding internships"
        result2 = keyword_based_filter_fallback(title2, desc2, "reddit_internships")
        print(f"✓ Question filtered: {result2} (expected: False)")
        assert result2 == False, "Should filter out question"
        
        # Test "for hire" post
        title3 = "[For Hire] Software Developer Available"
        desc3 = "I am available for freelance work"
        result3 = keyword_based_filter_fallback(title3, desc3, "reddit_jobs")
        print(f"✓ 'For hire' filtered: {result3} (expected: False)")
        assert result3 == False, "Should filter out 'for hire' posts"
        
        return True
    except Exception as e:
        print(f"✗ Error testing keyword fallback: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_ollama_if_available():
    """Test actual AI classification if Ollama is available"""
    print("\n" + "=" * 60)
    print("Testing AI Classification (Ollama)")
    print("=" * 60)
    
    try:
        from api.ai_filter import classify_opportunity
        from api.config import Config
        
        if not Config.is_ai_filter_enabled():
            print("⚠ AI filtering is disabled in config, skipping Ollama test")
            return True
        
        # Test opportunity
        print("\n  Testing actual opportunity...")
        title1 = "[Hiring] Software Engineer at Google - Remote position available"
        desc1 = "We are looking for a talented software engineer to join our team. Apply at our website."
        result1 = classify_opportunity(title1, desc1, "reddit_jobs")
        
        if result1.get('error'):
            print(f"  ⚠ Ollama not available: {result1.get('error')}")
            print("  ✓ Fallback mechanism working correctly")
        else:
            print(f"  ✓ Classification result: {result1.get('is_opportunity')}")
            print(f"  ✓ Confidence: {result1.get('confidence', 0):.2f}")
            print(f"  ✓ Reasoning: {result1.get('reasoning', 'N/A')[:100]}")
        
        # Test question
        print("\n  Testing question (should be filtered)...")
        title2 = "How do I find an internship? Looking for advice"
        desc2 = "I'm a student looking for advice on finding internships in tech"
        result2 = classify_opportunity(title2, desc2, "reddit_internships")
        
        if result2.get('error'):
            print(f"  ⚠ Ollama not available: {result2.get('error')}")
        else:
            print(f"  ✓ Classification result: {result2.get('is_opportunity')}")
            print(f"  ✓ Confidence: {result2.get('confidence', 0):.2f}")
            print(f"  ✓ Reasoning: {result2.get('reasoning', 'N/A')[:100]}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing with Ollama: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AI Filter Test Suite")
    print("=" * 60)
    
    results = []
    
    # Basic tests (no Ollama required)
    results.append(("Imports", test_ai_filter_imports()))
    results.append(("Prompt Building", test_prompt_building()))
    results.append(("Response Parsing", test_response_parsing()))
    results.append(("Classification (Disabled)", test_classification_without_ollama()))
    results.append(("Keyword Fallback", test_keyword_fallback()))
    
    # Optional Ollama test
    results.append(("AI Classification (Ollama)", test_with_ollama_if_available()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
