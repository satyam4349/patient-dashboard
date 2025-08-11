"""
Custom Gradio components for the Agent Companion Chatbot
This module provides a simple web interface using basic HTML and JavaScript
"""

import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import html

class GradioComponent:
    """Base class for all Gradio components"""
    def __init__(self, **kwargs):
        self.props = kwargs
        self.component_id = id(self)

class Textbox(GradioComponent):
    """Text input component"""
    def __init__(self, label="", value="", **kwargs):
        super().__init__(label=label, value=value, **kwargs)

class Radio(GradioComponent):
    """Radio button component"""
    def __init__(self, choices=None, value=None, label="", **kwargs):
        super().__init__(choices=choices or [], value=value, label=label, **kwargs)

class Chatbot(GradioComponent):
    """Chatbot display component"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Button(GradioComponent):
    """Button component"""
    def __init__(self, value="Button", **kwargs):
        super().__init__(value=value, **kwargs)
        self.click_handler = None
    
    def click(self, fn, inputs=None, outputs=None):
        """Set click handler for the button"""
        self.click_handler = {
            'fn': fn,
            'inputs': inputs or [],
            'outputs': outputs or []
        }

class State(GradioComponent):
    """State component for storing data"""
    def __init__(self, value=None, **kwargs):
        super().__init__(value=value, **kwargs)

class Markdown(GradioComponent):
    """Markdown display component"""
    def __init__(self, value="", **kwargs):
        super().__init__(value=value, **kwargs)

class Blocks:
    """Main container for Gradio interface"""
    
    def __init__(self):
        self.components = []
        self.current_components = {}
        self.handlers = {}
        
    def __enter__(self):
        # Store reference to current Blocks instance
        Blocks._current = self
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        Blocks._current = None
    
    def add_component(self, component):
        """Add a component to the interface"""
        self.components.append(component)
        return component
    
    def launch(self, server_port=7860, share=False):
        """Launch the web interface"""
        print(f"🚀 Starting Agent Companion Chatbot on http://localhost:{server_port}")
        
        # Create HTTP server
        server = HTTPServer(('localhost', server_port), self._create_handler())
        
        # Open browser
        webbrowser.open(f'http://localhost:{server_port}')
        
        print("Press Ctrl+C to stop the server")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            server.shutdown()
    
    def _create_handler(self):
        """Create HTTP request handler"""
        blocks_instance = self
        
        class GradioHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(blocks_instance._generate_html().encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path == '/chat':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode())
                    
                    # Process chat request
                    response = blocks_instance._handle_chat(data)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        return GradioHandler
    
    def _generate_html(self):
        """Generate HTML for the interface"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Agent Companion Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
        .chat-container { background: white; border: 1px solid #ddd; border-radius: 5px; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user-message { background: #e3f2fd; text-align: right; }
        .bot-message { background: #f1f8e9; text-align: left; }
        .input-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #45a049; }
        .radio-group { display: flex; gap: 15px; }
        .radio-group input { width: auto; margin-right: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Agent Companion Chatbot</h1>
        
        <div class="input-group">
            <label for="user_id">User ID:</label>
            <input type="text" id="user_id" value="user_001">
        </div>
        
        <div class="input-group">
            <label>LLM Backend:</label>
            <div class="radio-group">
                <label><input type="radio" name="backend" value="grok" checked> Grok</label>
                <label><input type="radio" name="backend" value="gemini"> Gemini</label>
            </div>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message bot-message">Hello! I'm your AI companion. How can I help you today?</div>
        </div>
        
        <div class="input-group">
            <label for="message">Your message:</label>
            <textarea id="message" rows="3" placeholder="Type your message here..."></textarea>
        </div>
        
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        let conversationHistory = [];
        let conversationId = null;

        function sendMessage() {
            const userId = document.getElementById('user_id').value;
            const backend = document.querySelector('input[name="backend"]:checked').value;
            const message = document.getElementById('message').value;
            
            if (!message.trim()) return;
            
            // Add user message to chat
            addMessageToChat(message, 'user');
            
            // Clear input
            document.getElementById('message').value = '';
            
            // Send to backend
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    backend: backend,
                    message: message,
                    history: conversationHistory,
                    conversation_id: conversationId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addMessageToChat(data.response, 'bot');
                    conversationHistory = data.history;
                    conversationId = data.conversation_id;
                } else {
                    addMessageToChat('Error: ' + data.error, 'bot');
                }
            })
            .catch(error => {
                addMessageToChat('Connection error: ' + error.message, 'bot');
            });
        }
        
        function addMessageToChat(message, sender) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = message;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Allow Enter to send message
        document.getElementById('message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>
        """
    
    def _handle_chat(self, data):
        """Handle chat requests"""
        try:
            # Import the chat function from gradio_app
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__ + '/..')))
            
            from gradio_app import chat
            
            user_id = data.get('user_id', 'user_001')
            backend = data.get('backend', 'grok')
            message = data.get('message', '')
            history = data.get('history', [])
            
            # Call the chat function
            agent_message, new_history, conversation_id = chat(user_id, backend, message, history)
            
            return {
                'success': True,
                'response': agent_message,
                'history': new_history,
                'conversation_id': conversation_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global reference to current Blocks instance
Blocks._current = None

# Override component creation to add to current Blocks
def _create_component(component_class):
    def wrapper(*args, **kwargs):
        component = component_class(*args, **kwargs)
        if hasattr(Blocks, '_current') and Blocks._current:
            Blocks._current.add_component(component)
        return component
    return wrapper

# Apply wrapper to all components
Textbox = _create_component(Textbox)
Radio = _create_component(Radio)
Chatbot = _create_component(Chatbot)
Button = _create_component(Button)
State = _create_component(State)
Markdown = _create_component(Markdown)