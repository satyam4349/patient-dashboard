import importlib
import sys
from typing import List, Tuple

def check_embedding_dependencies() -> List[Tuple[str, bool, str]]:
    """
    Check if all required embedding dependencies are installed and compatible.
    Returns: List of (package_name, is_available, version/error_message)
    """
    required_packages = [
        'sentence_transformers',
        'torch',
        'transformers',
        'numpy',
        'scikit-learn',
        'pandas',
        'nltk',
        'tqdm'
    ]
    
    results = []
    for package in required_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'unknown version')
            results.append((package, True, version))
        except ImportError as e:
            results.append((package, False, str(e)))
    
    return results

def verify_embedding_setup():
    """Verify embedding dependencies and print status."""
    print("Checking embedding dependencies...")
    results = check_embedding_dependencies()
    
    all_available = all(result[1] for result in results)
    
    print("\nDependency Status:")
    print("-----------------")
    for package, is_available, version_or_error in results:
        status = "✓" if is_available else "✗"
        message = version_or_error if is_available else f"Error: {version_or_error}"
        print(f"{status} {package}: {message}")
    
    if all_available:
        print("\n✅ All embedding dependencies are properly installed!")
        return True
    else:
        print("\n❌ Some dependencies are missing. Please install them using:")
        print("pip install -r requirements_embeddings.txt")
        return False

def install_embedding_dependencies():
    """Install required embedding dependencies."""
    import subprocess
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements_embeddings.txt"
        ], check=True)
        print("✅ Successfully installed embedding dependencies!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

if __name__ == "__main__":
    if not verify_embedding_setup():
        print("\nAttempting to install missing dependencies...")
        install_embedding_dependencies()
        verify_embedding_setup()
