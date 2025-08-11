"""
GAIA Enhanced Agent - Dependency Installation Script
This script installs all required dependencies for 40%+ GAIA benchmark performance
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Installing: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ SUCCESS: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {description}")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def install_system_dependencies():
    """Install system-level dependencies"""
    print("Installing system dependencies...")
    
    system = platform.system().lower()
    
    if system == "windows":
        print("Windows detected - installing Tesseract OCR...")
        print("Please download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("Make sure to add Tesseract to your PATH")
        
        # Try to install via chocolatey if available
        run_command("choco install tesseract", "Tesseract OCR via Chocolatey")
        
    elif system == "linux":
        print("Linux detected - installing system packages...")
        run_command("sudo apt-get update", "Update package list")
        run_command("sudo apt-get install -y tesseract-ocr tesseract-ocr-eng", "Tesseract OCR")
        run_command("sudo apt-get install -y ffmpeg", "FFmpeg for video processing")
        run_command("sudo apt-get install -y poppler-utils", "Poppler for PDF processing")
        
    elif system == "darwin":  # macOS
        print("macOS detected - installing via Homebrew...")
        run_command("brew install tesseract", "Tesseract OCR")
        run_command("brew install ffmpeg", "FFmpeg")
        run_command("brew install poppler", "Poppler")

def install_python_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    
    # Core dependencies
    dependencies = [
        # Core framework
        "gradio[oauth]>=5.35.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        
        # LangChain ecosystem
        "langchain>=0.1.0",
        "langchain-community>=0.0.20",
        "langchain-core>=0.1.0",
        "langchain-google-genai>=1.0.0",
        "langchain-huggingface>=0.0.3",
        "langgraph>=0.0.40",
        
        # API integrations
        "huggingface_hub>=0.19.0",
        "tavily-python>=0.3.0",
        "langchain-groq>=0.1.0",
        
        # Document processing
        "arxiv>=1.4.0",
        "wikipedia>=1.4.0",
        "pymupdf>=1.23.0",
        "openpyxl>=3.1.0",
        "xlrd>=2.0.0",
        "Pillow>=10.0.0",
        
        # Scientific computing
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "sympy>=1.12.0",
        "matplotlib>=3.7.0",
        
        # Video processing (FREE)
        "youtube-transcript-api>=0.6.0",
        "yt-dlp>=2023.12.30",
        
        # Advanced file processing (FREE)
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.10.0",
        "python-docx>=1.1.0",
        "python-pptx>=0.6.23",
        
        # OCR and image processing (FREE)
        "pytesseract>=0.3.10",
        "opencv-python>=4.8.0",
        "easyocr>=1.7.0",
        
        # Scientific computing (FREE)
        "biopython>=1.83",
        
        # Web scraping (FREE)
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        
        # Text processing (FREE)
        "nltk>=3.8.0",
        "textstat>=0.7.0",
        
        # Additional formats (FREE)
        "jsonlines>=4.0.0",
        "xmltodict>=0.13.0",
        "pyyaml>=6.0.0",
        
        # Network tools (FREE)
        "httpx>=0.25.0",
        "aiohttp>=3.9.0"
    ]
    
    # Install in batches to avoid overwhelming pip
    batch_size = 5
    for i in range(0, len(dependencies), batch_size):
        batch = dependencies[i:i+batch_size]
        command = f"pip install {' '.join(batch)}"
        run_command(command, f"Python dependencies batch {i//batch_size + 1}")

def download_nltk_data():
    """Download required NLTK data"""
    print("\nDownloading NLTK data...")
    
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        print("✅ NLTK data downloaded successfully")
    except Exception as e:
        print(f"❌ Failed to download NLTK data: {e}")

def setup_tesseract():
    """Setup Tesseract OCR configuration"""
    print("\nSetting up Tesseract OCR...")
    
    try:
        import pytesseract
        from PIL import Image
        
        # Test Tesseract installation
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        
        # On Windows, might need to set the path
        if platform.system().lower() == "windows":
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', ''))
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"✅ Tesseract path set to: {path}")
                    break
            else:
                print("⚠️  Tesseract not found in common locations. You may need to set the path manually.")
                
    except Exception as e:
        print(f"❌ Tesseract setup failed: {e}")

def verify_installation():
    """Verify that all components are working"""
    print("\n" + "="*50)
    print("VERIFYING INSTALLATION")
    print("="*50)
    
    tests = [
        ("YouTube Transcript API", "youtube_transcript_api", "YouTubeTranscriptApi"),
        ("yt-dlp", "yt_dlp", "YoutubeDL"),
        ("PDF Processing", "PyPDF2", "PdfReader"),
        ("PDF Advanced", "pdfplumber", "PDF"),
        ("Word Documents", "docx", "Document"),
        ("OCR - Tesseract", "pytesseract", "image_to_string"),
        ("OCR - EasyOCR", "easyocr", "Reader"),
        ("Computer Vision", "cv2", "imread"),
        ("Biopython", "Bio.PDB", "PDBParser"),
        ("Web Scraping", "bs4", "BeautifulSoup"),
        ("Selenium", "selenium", "webdriver"),
        ("Scientific Computing", "scipy", "stats"),
        ("Symbolic Math", "sympy", "Symbol"),
    ]
    
    results = []
    for name, module, attribute in tests:
        try:
            mod = __import__(module, fromlist=[attribute])
            getattr(mod, attribute)
            print(f"✅ {name}: OK")
            results.append(True)
        except ImportError:
            print(f"❌ {name}: Module not found")
            results.append(False)
        except AttributeError:
            print(f"⚠️  {name}: Module found but attribute missing")
            results.append(False)
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n{'='*50}")
    print(f"INSTALLATION SUMMARY")
    print(f"{'='*50}")
    print(f"Success rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    if success_rate >= 80:
        print("🎉 Installation mostly successful! Ready for GAIA benchmark.")
    elif success_rate >= 60:
        print("⚠️  Installation partially successful. Some features may not work.")
    else:
        print("❌ Installation failed. Please check errors above.")
    
    return success_rate >= 60

def main():
    """Main installation function"""
    print("🚀 GAIA Enhanced Agent - Dependency Installation")
    print("This will install all dependencies needed for 40%+ GAIA benchmark performance")
    print("="*70)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python dependencies
    install_python_dependencies()
    
    # Download NLTK data
    download_nltk_data()
    
    # Setup Tesseract
    setup_tesseract()
    
    # Verify installation
    success = verify_installation()
    
    if success:
        print("\n🎉 Installation complete! You can now run the GAIA Enhanced Agent.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your API keys")
        print("2. Run: python app.py")
        print("3. Test with: python gaia_enhanced_agent.py")
    else:
        print("\n❌ Installation incomplete. Please check errors above.")
    
    return success

if __name__ == "__main__":
    main()