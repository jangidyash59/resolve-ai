#!/usr/bin/env python3
"""
Test script to verify Gemini API connection and embedding generation
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Testing Gemini API Connection")
print("=" * 60)

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not set in .env file")
    sys.exit(1)

print(f"✓ API Key found: {api_key[:10]}...{api_key[-10:]}")
print(f"  Key format: {'AQ. (new auth key)' if api_key.startswith('AQ.') else 'AIza (legacy)'}")

# Test embedding generation
try:
    from google import genai
    
    print("\n" + "=" * 60)
    print("Testing Gemini Client Initialization")
    print("=" * 60)
    
    client = genai.Client(api_key=api_key)
    print("✓ Gemini client initialized successfully")
    
    print("\n" + "=" * 60)
    print("Testing Embedding Generation")
    print("=" * 60)
    
    test_text = "This is a test for return policy"
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    
    print(f"  Model: {embedding_model}")
    print(f"  Test text: '{test_text}'")
    
    response = client.models.embed_content(
        model=embedding_model,
        contents=test_text
    )
    
    embedding = response.embeddings[0].values
    print(f"✓ Embedding generated successfully")
    print(f"  Dimension: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Gemini API is working correctly")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Verify GEMINI_API_KEY is correct (get from https://aistudio.google.com/)")
    print("2. Check if your API key has embeddings enabled")
    print("3. Verify you have quota remaining")
    print("4. Make sure google-genai library is installed: pip install google-genai")
    sys.exit(1)
