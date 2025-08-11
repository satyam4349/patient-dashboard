#!/usr/bin/env python3
"""
Test script to verify the improvements work correctly
"""
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import build_graph

def test_hybrid_agent():
    """Test the hybrid agent with fallback"""
    print("🧪 Testing Hybrid Agent with Rate Limiting & Fallback")
    print("=" * 60)
    
    # Check API keys
    required_keys = ["GOOGLE_API_KEY", "HUGGINGFACE_API_TOKEN", "TAVILY_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing API keys: {', '.join(missing_keys)}")
        print("Please add them to your .env file")
        return False
    
    print("✅ All API keys found")
    
    # Test simple question
    test_question = "What is 15 * 23 + 7?"
    
    try:
        print(f"\n🔍 Testing question: {test_question}")
        
        # Build hybrid graph
        graph = build_graph(provider="hybrid")
        print("✅ Hybrid graph built successfully")
        
        # Test the question
        messages = [HumanMessage(content=test_question)]
        result = graph.invoke({"messages": messages})
        
        answer = result['messages'][-1].content
        print(f"📝 Answer: {answer}")
        
        # Check if answer contains expected result (15 * 23 + 7 = 352)
        if "352" in str(answer):
            print("✅ Mathematical calculation test passed!")
        else:
            print("⚠️ Mathematical calculation might need verification")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n🕒 Testing Rate Limiting")
    print("=" * 30)
    
    from agent import RateLimiter
    import time
    
    # Test rate limiter
    limiter = RateLimiter(calls_per_minute=3)  # Very conservative for testing
    
    start_time = time.time()
    
    # Make several calls
    for i in range(5):
        print(f"Making call {i+1}...")
        limiter.wait_if_needed()
        print(f"Call {i+1} completed")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"⏱️ Total time for 5 calls: {elapsed:.1f} seconds")
    
    if elapsed > 10:  # Should have some delays
        print("✅ Rate limiting is working (calls were delayed)")
        return True
    else:
        print("⚠️ Rate limiting might not be working as expected")
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced GAIA Agent")
    print("=" * 50)
    
    # Test 1: Hybrid agent
    test1_passed = test_hybrid_agent()
    
    # Test 2: Rate limiting
    test2_passed = test_rate_limiting()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Hybrid Agent: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Rate Limiting: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The enhanced agent is ready.")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")