import gradio as gr
from services.agent_companion_service import AgentCompanionService

agent = AgentCompanionService()

def chat(user_id, backend, message, history):
    """
    Chat function expected by components.py
    Returns: (agent_message, new_history, conversation_id)
    """
    # Convert backend name if needed
    if backend == 'grok':
        backend = 'groq'
    
    # Get conversation_id from history if available (we'll use None for new conversations)
    conversation_id = None
    
    # Call the existing chat_with_agent function
    new_history, new_conversation_id = chat_with_agent(message, history, user_id, backend, conversation_id)
    
    # Get the agent's last message
    if new_history and len(new_history) > 0:
        agent_message = new_history[-1][1]  # Get the agent's response from the last exchange
    else:
        agent_message = "I'm sorry, I couldn't process your message."
    
    return agent_message, new_history, new_conversation_id

def chat_with_agent(message, history, user_id, backend, conversation_id):
    if not message.strip():
        return history, conversation_id
    
    if not conversation_id:
        # Start new conversation
        convo = agent.start_conversation(user_id, message, llm_backend=backend)
        conversation_id = convo.conversation_id
        agent_message = convo.messages[-1].message
    else:
        # Continue existing conversation
        convo = agent.continue_conversation(conversation_id, message)
        if convo:
            agent_message = convo.messages[-1].message
        else:
            # If conversation not found, start new one
            convo = agent.start_conversation(user_id, message, llm_backend=backend)
            conversation_id = convo.conversation_id
            agent_message = convo.messages[-1].message
    
    # Update history
    history.append([message, agent_message])
    return history, conversation_id

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Agent Companion Chatbot")
    
    user_id = gr.Textbox(label="User ID", value="user_001")
    backend = gr.Radio(choices=["groq", "gemini"], value="groq", label="LLM Backend")
    
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your message", placeholder="Type your message here...")
    send_btn = gr.Button("Send")
    
    # State variables
    conversation_id = gr.State(None)
    
    def send_message(message, history, user_id, backend, conversation_id):
        # Call the chat function
        new_history, new_conversation_id = chat_with_agent(message, history, user_id, backend, conversation_id)
        # Clear the message box by returning empty string
        return new_history, new_conversation_id, ""
    
    send_btn.click(
        send_message,
        inputs=[msg, chatbot, user_id, backend, conversation_id],
        outputs=[chatbot, conversation_id, msg]
    )

if __name__ == "__main__":
    demo.launch()
