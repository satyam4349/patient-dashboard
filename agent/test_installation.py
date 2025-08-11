#!/usr/bin/env python3
"""
Test script to verify that all dependencies are properly installed
and the agent companion system is working correctly.
"""

import sys
import traceback
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("gradio", "Web interface"),
        ("requests", "HTTP client"),
        ("pandas", "Data processing"),
        ("dotenv", "Environment variables"),
        ("typing_extensions", "Type hints"),
    ]
    
    failed_imports = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}: {description}")
        except ImportError as e:
            print(f"  ❌ {module_name}: FAILED - {e}")
            failed_imports.append(module_name)
    
    return failed_imports

def test_local_modules():
    """Test that local modules can be imported."""
    print("\n🏠 Testing local module imports...")
    
    local_modules = [
        ("models.agent_companion_models", "Data models"),
        ("services.agent_companion_service", "Agent service"),
        ("services.llm_service", "LLM service"),
        ("services.journal_data_service", "Journal service"),
    ]
    
    failed_imports = []
    
    for module_name, description in local_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}: {description}")
        except ImportError as e:
            print(f"  ❌ {module_name}: FAILED - {e}")
            failed_imports.append(module_name)
    
    return failed_imports

def test_basic_functionality():
    """Test basic functionality of the agent companion system."""
    print("\n⚙️ Testing basic functionality...")
    
    try:
        # Test Pydantic models
        from models.agent_companion_models import JournalEntry, ChatMessage, AgentConversation
        
        # Create test journal entry
        test_entry = JournalEntry(
            user_id="test_user",
            disorder_prediction="None",
            journal_entry="Test journal entry for validation",
            detected_markers=["test_marker_1", "test_marker_2"],
            check_in_question="How are you feeling today?"
        )
        print("  ✅ Pydantic models working correctly")
        
        # Test chat message
        test_message = ChatMessage(
            sender="user",
            message="Hello, agent!",
            timestamp=datetime.now()
        )
        print("  ✅ Chat message model working correctly")
        
        # Test conversation model
        test_conversation = AgentConversation(
            conversation_id="test_conv_001",
            user_id="test_user",
            messages=[test_message],
            context="Test context",
            llm_backend="grok"
        )
        print("  ✅ Conversation model working correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_services():
    """Test that services can be instantiated."""
    print("\n🔧 Testing service instantiation...")
    
    try:
        from services.journal_data_service import JournalDataService
        journal_service = JournalDataService()
        print("  ✅ Journal data service instantiated")
        
        from services.llm_service import LLMService
        llm_service = LLMService()
        print("  ✅ LLM service instantiated")
        
        from services.agent_companion_service import AgentCompanionService
        agent_service = AgentCompanionService()
        print("  ✅ Agent companion service instantiated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service instantiation failed: {e}")
        traceback.print_exc()
        return False

def test_gradio_app():
    """Test that the Gradio app can be imported."""
    print("\n🌐 Testing Gradio app...")
    
    try:
        import gradio_app
        print("  ✅ Gradio app imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Gradio app import failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Agent Companion Installation Test")
    print("=" * 40)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print("=" * 40)
    
    # Run all tests
    failed_external = test_imports()
    failed_local = test_local_modules()
    basic_functionality_ok = test_basic_functionality()
    services_ok = test_services()
    gradio_ok = test_gradio_app()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 20)
    
    if not failed_external:
        print("✅ All external dependencies imported successfully")
    else:
        print(f"❌ Failed external imports: {', '.join(failed_external)}")
    
    if not failed_local:
        print("✅ All local modules imported successfully")
    else:
        print(f"❌ Failed local imports: {', '.join(failed_local)}")
    
    if basic_functionality_ok:
        print("✅ Basic functionality tests passed")
    else:
        print("❌ Basic functionality tests failed")
    
    if services_ok:
        print("✅ Service instantiation tests passed")
    else:
        print("❌ Service instantiation tests failed")
    
    if gradio_ok:
        print("✅ Gradio app import test passed")
    else:
        print("❌ Gradio app import test failed")
    
    # Overall result
    all_tests_passed = (
        not failed_external and 
        not failed_local and 
        basic_functionality_ok and 
        services_ok and 
        gradio_ok
    )
    
    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED! Your agent companion is ready to use!")
        print("\nTo run the agent companion:")
        print("  python gradio_app.py")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're in the activated virtual environment")
        print("2. Try reinstalling dependencies: pip install -r requirements.txt")
        print("3. Check that all files are in the correct locations")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)