#!/usr/bin/env python3
"""
Verify Ollama/Llama is installed and the AI filter can use it.
Run this after installing Ollama: python3 verify_ollama.py
"""
import sys
import urllib.request
import json

def check_ollama_running():
    """Check if Ollama server is running"""
    try:
        req = urllib.request.Request('http://localhost:11434/api/tags')
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            models = data.get('models', [])
            names = [m.get('name', '') for m in models]
            return True, names
    except Exception as e:
        return False, str(e)

def test_ai_filter():
    """Test the AI filter with Ollama"""
    try:
        from api.ai_filter import classify_opportunity
        from api.config import Config
        
        # Test with a question (should classify as false)
        result = classify_opportunity(
            "How do I find an internship? Looking for advice",
            "I'm a student looking for advice on finding internships",
            "reddit_internships"
        )
        
        if result.get('error'):
            return False, result.get('error')
        
        is_opp = result.get('is_opportunity')
        confidence = result.get('confidence', 0)
        reasoning = result.get('reasoning', '')[:80]
        
        return True, {
            'is_opportunity': is_opp,
            'confidence': confidence,
            'reasoning': reasoning,
            'expected_question': not is_opp  # We expect False for a question
        }
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Ollama / AI Filter Verification")
    print("=" * 60)
    
    # 1. Check Ollama server
    print("\n1. Checking Ollama server (http://localhost:11434)...")
    ok, data = check_ollama_running()
    if ok:
        print(f"   ✓ Ollama is running")
        if isinstance(data, list) and data:
            print(f"   ✓ Models available: {', '.join(data)}")
            if not any('llama' in m.lower() for m in data):
                print("   ⚠ No 'llama' model in list. Run: ollama pull llama2")
        else:
            print("   ⚠ No models listed. Run: ollama pull llama2")
    else:
        print(f"   ✗ Ollama not reachable: {data}")
        print("\n   To fix:")
        print("   - Start Ollama: ollama serve")
        print("   - Or install: brew install ollama  (macOS)")
        return 1
    
    # 2. Test AI filter
    print("\n2. Testing AI filter with sample text...")
    print("   (First run can take 30–90 seconds while the model loads; timeout is 120s)")
    ok, data = test_ai_filter()
    if ok and isinstance(data, dict):
        print(f"   ✓ AI filter responded")
        print(f"   - Question classified as opportunity: {data.get('is_opportunity')}")
        print(f"   - Confidence: {data.get('confidence', 0):.2f}")
        print(f"   - Reasoning: {data.get('reasoning', '')}...")
        if data.get('expected_question') is True:
            print("   ✓ Question correctly classified (not an opportunity)")
        else:
            print("   ⚠ Expected question to be filtered; check prompt/model")
    elif ok:
        print(f"   Result: {data}")
    else:
        print(f"   ✗ AI filter error: {data}")
        return 1
    
    print("\n" + "=" * 60)
    print("Setup looks good. Re-fetch opportunities to use AI filtering.")
    print("=" * 60)
    return 0

if __name__ == '__main__':
    sys.exit(main())
