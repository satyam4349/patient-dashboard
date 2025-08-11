import gradio as gr
from services.agent_companion_service import AgentCompanionService

agent = AgentCompanionService()

def chat(user_id, backend, message, history):
    if not history:
        convo = agent.start_conversation(user_id, message, llm_backend=backend)
        conversation_id = convo.conversation_id
        agent_message = convo.messages[-1].message
        return agent_message, [[message, agent_message]], conversation_id
    else:
        conversation_id = history[-1][2] if len(history[-1]) > 2 else None
        if not conversation_id:
            convo = agent.start_conversation(user_id, message, llm_backend=backend)
            conversation_id = convo.conversation_id
            agent_message = convo.messages[-1].message
            return agent_message, [[message, agent_message, conversation_id]], conversation_id
        convo = agent.continue_conversation(conversation_id, message)
        agent_message = convo.messages[-1].message
        history.append([message, agent_message, conversation_id])
        return agent_message, history, conversation_id

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Agent Companion Chatbot")
    user_id = gr.Textbox(label="User ID", value="user_001")
    backend = gr.Radio(choices=["grok", "gemini"], value="grok", label="LLM Backend")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your message")
    conversation_id = gr.State(None)
    history = gr.State([])

    def respond(user_id, backend, msg, history, conversation_id):
        agent_message, new_history, new_convo_id = chat(user_id, backend, msg, history)
        return agent_message, new_history, new_convo_id

    send = gr.Button("Send")
    send.click(
        respond,
        inputs=[user_id, backend, msg, history, conversation_id],
        outputs=[chatbot, history, conversation_id]
    )

if __name__ == "__main__":
    demo.launch()
