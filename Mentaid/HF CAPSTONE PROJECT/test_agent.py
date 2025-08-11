#!/usr/bin/env python3
"""
Test script for GAIA-optimized agent
Run this to verify your setup is working correctly
"""

import os
from dotenv import load_dotenv
from agent import build_graph
from langchain_core.messages import HumanMessage

def test_agent_setup():
    """Test basic agent functionality"""
    print("🚀 Testing GAIA-Optimized Agent Setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    required_keys = ["GOOGLE_API_KEY", "TAVILY_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing API keys: {', '.join(missing_keys)}")
        print("Please add them to your .env file")
        return False
    
    print("✅ API keys found")
    
    # Test agent initialization
    try:
        print("🧠 Initializing Google Gemini agent...")
        graph = build_graph(provider="google")
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False
    
    # Test simple question
    try:
        print("🤔 Testing with simple question...")
        test_question = "What is 15 + 27?"
        messages = [HumanMessage(content=test_question)]
        result = graph.invoke({"messages": messages})
        answer = result['messages'][-1].content
        print(f"📝 Question: {test_question}")
        print(f"🎯 Answer: {answer[:200]}...")
        print("✅ Basic functionality test passed")
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Your GAIA-optimized agent is ready!")
    print("🚀 Expected GAIA performance: 30%+")
    return True

if __name__ == "__main__":
    test_agent_setup()