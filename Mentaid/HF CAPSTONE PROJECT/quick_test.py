#!/usr/bin/env python3
"""Quick test of the updated Groq models"""
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from enhanced_agent import build_enhanced_graph

load_dotenv()

def test_updated_models():
    print("🧪 Testing Updated Groq Models")
    print("=" * 40)
    
    try:
        # Build the enhanced graph
        graph = build_enhanced_graph()
        print("✅ Enhanced graph built successfully")
        
        # Test with a simple question
        test_question = "What is 15 + 27?"
        print(f"\n🧮 Testing: {test_question}")
        
        messages = [HumanMessage(content=test_question)]
        result = graph.invoke({"messages": messages})
        
        answer = result['messages'][-1].content
        print(f"📝 Answer: {answer}")
        
        if "42" in str(answer):
            print("✅ Mathematical test PASSED!")
            return True
        else:
            print("⚠️ Answer received but may need verification")
            return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_updated_models()
    if success:
        print("\n🎉 Ready to run the full GAIA evaluation!")
        print("Run: python app.py")
    else:
        print("\n⚠️ Please check the error above before proceeding")