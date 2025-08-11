#!/usr/bin/env python3
"""
Simple startup script for the Agent Companion
"""
import os
import sys

def main():
    print("🤖 Starting Agent Companion...")
    
    # Check if we're in the right directory
    if not os.path.exists("gradio_app.py"):
        print("❌ Error: Please run this script from the agent directory")
        print("Current directory:", os.getcwd())
        return
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found")
        print("Please copy .env.example to .env and add your API keys")
        if os.path.exists(".env.example"):
            print("Run: copy .env.example .env")
        return
    
    # Import and run the gradio app
    try:
        print("🚀 Loading Gradio interface...")
        import gradio_app
        print("✅ Agent Companion is ready!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements_clean.txt")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")

if __name__ == "__main__":
    main()