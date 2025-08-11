# 🤖 Agent Companion - Mental Health Assistant

A sophisticated AI-powered companion that provides personalized mental health support by analyzing journal entries and engaging in meaningful conversations.

## 🚀 Quick Start

### Prerequisites
- Python 3.13.6 (recommended)
- Windows PowerShell (for automated installation)

### Automated Installation (Recommended)

1. **Navigate to the agent directory:**
   ```powershell
   cd "c:\Users\DELL\Downloads\IEEE Techsangam\demo dashboard\patient-dashboard\agent"
   ```

2. **Run the automated installation script:**
   ```powershell
   .\install_dependencies.ps1
   ```

3. **Test the installation:**
   ```powershell
   python test_installation.py
   ```

4. **Set up your API keys:**
   ```powershell
   copy .env.example .env
   # Edit .env file with your actual API keys
   ```

5. **Run the application:**
   ```powershell
   python gradio_app.py
   ```

### Manual Installation (Alternative)

If the automated script doesn't work, follow these steps:

1. **Create and activate virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Upgrade pip and install build tools:**
   ```powershell
   python -m pip install --upgrade pip
   pip install --upgrade wheel setuptools
   ```

3. **Install dependencies:**
   ```powershell
   # For full installation:
   pip install -r requirements.txt

   # For minimal installation:
   pip install -r requirements_minimal.txt
   ```

4. **Verify installation:**
   ```powershell
   python test_installation.py
   ```

## 📋 Features

- **🧠 AI-Powered Conversations**: Supports both Grok and Gemini LLM backends
- **📖 Journal Analysis**: Analyzes user journal entries for context-aware responses
- **🌐 Web Interface**: Beautiful Gradio-based web interface
- **🔒 Privacy-Focused**: Local processing with secure API integration
- **📊 Mental Health Tracking**: Mood, stress, anxiety, and depression level tracking
- **🎯 Personalized Support**: Tailored responses based on user history

## 🛠️ Technical Architecture

### Core Components

1. **Agent Companion Service** (`services/agent_companion_service.py`)
   - Manages conversations and context
   - Integrates journal data with LLM responses

2. **LLM Service** (`services/llm_service.py`)
   - Handles communication with Grok and Gemini APIs
   - Provides fallback and error handling

3. **Journal Data Service** (`services/journal_data_service.py`)
   - Processes CSV-based journal entries
   - Provides user-specific data retrieval

4. **Data Models** (`models/agent_companion_models.py`)
   - Pydantic models for type safety
   - Structured data validation

### API Endpoints

- `POST /agent-companion/start` - Start a new conversation
- `POST /agent-companion/continue` - Continue existing conversation
- `GET /agent-companion/conversation/{id}` - Retrieve conversation

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required: API Keys
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Configuration
DEBUG=True
```

### API Key Setup

1. **Groq API Key:**
   - Visit [Groq Console](https://console.groq.com)
   - Create an account and generate an API key
   - Add to your `.env` file

2. **Google API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Add to your `.env` file

## 📊 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for APIs
- **Gradio**: Web interface for ML applications
- **Pydantic**: Data validation and settings management
- **Pandas**: Data processing and analysis
- **Requests**: HTTP library for API calls

### Full Dependency List
See `requirements.txt` for the complete list of pinned dependencies optimized for Python 3.13 compatibility.

## 🧪 Testing

Run the comprehensive test suite:

```powershell
python test_installation.py
```

This will verify:
- ✅ All dependencies are properly installed
- ✅ Local modules can be imported
- ✅ Basic functionality works
- ✅ Services can be instantiated
- ✅ Gradio app can be loaded

## 🚨 Troubleshooting

### Common Issues

1. **"No module named 'requests'" Error**
   - **Cause**: Virtual environment not properly activated
   - **Solution**: Run `.\venv\Scripts\Activate.ps1` and reinstall dependencies

2. **"Defaulting to user installation" Warning**
   - **Cause**: Virtual environment not activated or permissions issue
   - **Solution**: Delete `venv` folder and run `install_dependencies.ps1`

3. **Dependency Conflicts**
   - **Cause**: Incompatible package versions
   - **Solution**: Use `requirements_minimal.txt` for basic functionality

4. **API Key Errors**
   - **Cause**: Missing or invalid API keys
   - **Solution**: Check `.env` file and verify API key validity

### Version Compatibility

This project is optimized for:
- **Python**: 3.13.6
- **FastAPI**: 0.115.x
- **Gradio**: 5.42.x
- **Pydantic**: 2.11.x

## 📁 Project Structure

```
agent/
├── models/
│   └── agent_companion_models.py    # Data models
├── services/
│   ├── agent_companion_service.py   # Main service logic
│   ├── llm_service.py              # LLM integration
│   └── journal_data_service.py     # Journal processing
├── routes/
│   └── agent_companion_routes.py   # FastAPI routes
├── gradio/
│   └── components.py               # Gradio components
├── gradio_app.py                   # Main Gradio application
├── requirements.txt                # Full dependencies
├── requirements_minimal.txt        # Minimal dependencies
├── install_dependencies.ps1        # Automated installer
├── test_installation.py           # Test suite
├── .env.example                   # Environment template
└── README.md                      # This file
```

## 🤝 Usage Examples

### Starting a Conversation

```python
from services.agent_companion_service import AgentCompanionService

agent = AgentCompanionService()
conversation = agent.start_conversation(
    user_id="user_001",
    initial_message="I'm feeling anxious today",
    llm_backend="grok"
)
print(conversation.messages[-1].message)
```

### Web Interface

1. Run `python gradio_app.py`
2. Open your browser to the displayed URL
3. Enter your User ID
4. Select LLM backend (Grok or Gemini)
5. Start chatting with your AI companion

## 📝 License

This project is part of the MentAid mental health platform. Please refer to the main project license.

## 🆘 Support

If you encounter issues:

1. Run the test suite: `python test_installation.py`
2. Check the troubleshooting section above
3. Verify your Python version: `python --version`
4. Ensure virtual environment is activated
5. Try the minimal installation: `pip install -r requirements_minimal.txt`

---

**Made with ❤️ for mental health support**