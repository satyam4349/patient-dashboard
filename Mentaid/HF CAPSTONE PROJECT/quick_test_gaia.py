"""
Quick Test for GAIA Enhanced Agent
Tests basic functionality without requiring all dependencies
"""

import sys
import os

def test_imports():
    """Test if core modules can be imported"""
    print("Testing core imports...")
    
    try:
        from gaia_enhanced_agent import GAIAEnhancedAgent
        print("✅ GAIA Enhanced Agent imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import GAIA Enhanced Agent: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing GAIA Enhanced Agent: {e}")
        return False

def test_basic_functionality():
    """Test basic agent functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from gaia_enhanced_agent import GAIAEnhancedAgent
        
        # Initialize agent
        agent = GAIAEnhancedAgent()
        print("✅ Agent initialized successfully")
        
        # Test simple question
        test_question = "What is 2 + 2?"
        print(f"Testing question: {test_question}")
        
        response = agent.process_question(test_question)
        print(f"Response: {response}")
        
        if "4" in str(response):
            print("✅ Basic math test passed")
            return True
        else:
            print("❌ Basic math test failed")
            return False
            
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_availability():
    """Test which tools are available"""
    print("\nTesting tool availability...")
    
    tools_status = {
        "YouTube Processing": False,
        "PDF Processing": False,
        "OCR": False,
        "Biopython": False,
        "Web Scraping": False
    }
    
    # Test YouTube processing
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        import yt_dlp
        tools_status["YouTube Processing"] = True
        print("✅ YouTube processing available")
    except ImportError:
        print("❌ YouTube processing not available")
    
    # Test PDF processing
    try:
        import PyPDF2
        import pdfplumber
        tools_status["PDF Processing"] = True
        print("✅ PDF processing available")
    except ImportError:
        print("❌ PDF processing not available")
    
    # Test OCR
    try:
        import pytesseract
        import cv2
        import easyocr
        tools_status["OCR"] = True
        print("✅ OCR available")
    except ImportError:
        print("❌ OCR not available")
    
    # Test Biopython
    try:
        from Bio.PDB import PDBParser
        tools_status["Biopython"] = True
        print("✅ Biopython available")
    except ImportError:
        print("❌ Biopython not available")
    
    # Test Web Scraping
    try:
        from bs4 import BeautifulSoup
        import requests
        tools_status["Web Scraping"] = True
        print("✅ Web scraping available")
    except ImportError:
        print("❌ Web scraping not available")
    
    available_count = sum(tools_status.values())
    total_count = len(tools_status)
    
    print(f"\nTool availability: {available_count}/{total_count} ({available_count/total_count*100:.1f}%)")
    
    return available_count >= 2  # At least 2 tools should be available

def main():
    """Main test function"""
    print("🔧 GAIA Enhanced Agent - Quick Test")
    print("="*40)
    
    # Test imports
    import_success = test_imports()
    if not import_success:
        print("\n❌ Import test failed. Please install dependencies:")
        print("python install_gaia_dependencies.py")
        return False
    
    # Test tool availability
    tools_success = test_tool_availability()
    if not tools_success:
        print("\n⚠️  Limited tools available. Some features may not work.")
    
    # Test basic functionality
    basic_success = test_basic_functionality()
    
    print("\n" + "="*40)
    print("QUICK TEST SUMMARY")
    print("="*40)
    
    if import_success and basic_success:
        print("🎉 Quick test PASSED! Agent is ready for use.")
        if tools_success:
            print("✅ Most tools are available for full functionality.")
        else:
            print("⚠️  Limited tools available. Install more dependencies for full functionality.")
        
        print("\nNext steps:")
        print("1. Make sure your .env file has API keys")
        print("2. Run: python app.py")
        print("3. For full testing: python test_gaia_capabilities.py")
        
        return True
    else:
        print("❌ Quick test FAILED!")
        print("\nTroubleshooting:")
        print("1. Install dependencies: python install_gaia_dependencies.py")
        print("2. Check your .env file has correct API keys")
        print("3. Verify Python version is 3.8+")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)