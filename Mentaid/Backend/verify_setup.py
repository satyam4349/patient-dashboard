#!/usr/bin/env python3
"""
Verification script for Backend requirements compatibility
Run this after installing requirements.txt to ensure no conflicts
"""

import sys
import importlib
import pkg_resources

def check_import(module_name, display_name=None):
    """Check if module can be imported and get version"""
    if display_name is None:
        display_name = module_name
    
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"✅ {display_name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {display_name}: Import failed - {e}")
        return False

def check_compatibility():
    """Check critical compatibility requirements"""
    print("🔍 Checking Backend Requirements Compatibility...\n")
    
    # Core API Framework
    print("📡 API Framework:")
    check_import('fastapi', 'FastAPI')
    check_import('uvicorn', 'Uvicorn')
    check_import('pydantic', 'Pydantic')
    
    # Database & Auth
    print("\n🔐 Database & Auth:")
    check_import('supabase', 'Supabase')
    check_import('jose', 'Python-JOSE')
    check_import('bcrypt', 'BCrypt')
    
    # AI/ML Core
    print("\n🤖 AI/ML Stack:")
    check_import('numpy', 'NumPy')
    check_import('pandas', 'Pandas')
    check_import('sklearn', 'Scikit-learn')
    check_import('torch', 'PyTorch')
    check_import('transformers', 'Transformers')
    
    # Agent System
    print("\n🤝 Agent System:")
    check_import('langchain', 'LangChain')
    check_import('langgraph', 'LangGraph')
    check_import('langchain_google_genai', 'LangChain Google GenAI')
    
    # NLP Libraries
    print("\n📝 NLP Libraries:")
    check_import('spacy', 'spaCy')
    check_import('nltk', 'NLTK')
    check_import('sentence_transformers', 'Sentence Transformers')
    
    # Visualization
    print("\n📊 Visualization:")
    check_import('matplotlib', 'Matplotlib')
    check_import('plotly', 'Plotly')
    check_import('seaborn', 'Seaborn')
    
    # Frontend Integration
    print("\n🖥️ Frontend Integration:")
    check_import('gradio', 'Gradio')
    check_import('streamlit', 'Streamlit')
    
    print("\n" + "="*50)
    
    # Check for known conflicts
    print("🔍 Checking for Known Conflicts...")
    
    try:
        import numpy as np
        import torch
        import sklearn
        
        print(f"✅ NumPy-PyTorch compatibility: NumPy {np.__version__} + PyTorch {torch.__version__}")
        print(f"✅ NumPy-Sklearn compatibility: NumPy {np.__version__} + Sklearn {sklearn.__version__}")
        
        # Test basic operations
        import torch
        tensor = torch.tensor([1, 2, 3])
        numpy_array = tensor.numpy()
        print("✅ PyTorch-NumPy conversion: OK")
        
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(n_estimators=2)
        print("✅ Scikit-learn model creation: OK")
        
    except Exception as e:
        print(f"❌ Compatibility issue detected: {e}")
    
    print("\n🎉 Compatibility check complete!")
    print("If you see any ❌ errors above, please report them.")

if __name__ == "__main__":
    check_compatibility()