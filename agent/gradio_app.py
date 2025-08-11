
import gradio as gr

# New companion agent (Groq 70B by default, rolling memory, follow-ups)
from companion_agent.service import CompanionService

companion = CompanionService()


def _format_recent_context_markdown(conversation_id: str) -> str:
    state = companion.memory.get(conversation_id) if conversation_id else None
    if not state:
        return ""
    lines = ["### Recent context"]
    if state.summary:
        lines.append(f"Summary: {state.summary}\n")
    # Show last 4 turns
    for turn in state.messages[-4:]:
        role = "You" if turn.role == "user" else "Assistant"
        lines.append(f"- **{role}**: {turn.content}")
    return "\n".join(lines)


def chat_with_agent(message, history, user_id, conversation_id):
    if not message or not message.strip():
        # keep modal hidden
        return history, conversation_id, gr.update(visible=False), "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

    if not conversation_id:
        # Start new conversation
        state = companion.start_conversation(user_id, message)
        conversation_id = state.conversation_id
        agent_message = state.messages[-1].content
    else:
        # Continue existing conversation
        state = companion.continue_conversation(conversation_id, message)
        if state:
            agent_message = state.messages[-1].content
        else:
            # If conversation not found, start new one
            state = companion.start_conversation(user_id, message)
            conversation_id = state.conversation_id
            agent_message = state.messages[-1].content

    # Update visible history in UI
    # Gradio Chatbot(type='messages') expects list[dict{role, content}] in v5
    if history is None:
        history = []
    # Normalize: if previous code put tuples, flatten them into message dicts
    normalized = []
    for item in history:
        if isinstance(item, dict) and 'role' in item and 'content' in item:
            normalized.append(item)
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            # classic (user, assistant) pair -> expand to two message dicts
            u, a = item
            if isinstance(u, str) and u:
                normalized.append({"role": "user", "content": u})
            if isinstance(a, str) and a:
                normalized.append({"role": "assistant", "content": a})
        else:
            # fallback: stringify
            normalized.append({"role": "assistant", "content": str(item)})
    # append current turn
    normalized.append({"role": "user", "content": message})
    normalized.append({"role": "assistant", "content": agent_message})

    # Modal visibility & question text
    show_modal = gr.update(visible=False)
    modal_question = ""
    if state and getattr(state, "pending_yes_no", False) and state.pending_yes_no_question:
        show_modal = gr.update(visible=True)
        modal_question = state.pending_yes_no_question

    # Follow-ups
    f1 = gr.update(visible=False)
    f2 = gr.update(visible=False)
    f3 = gr.update(visible=False)
    if state and state.suggested_followups:
        items = state.suggested_followups[:3]
        if len(items) > 0:
            f1 = gr.update(value=items[0], visible=True)
        if len(items) > 1:
            f2 = gr.update(value=items[1], visible=True)
        if len(items) > 2:
            f3 = gr.update(value=items[2], visible=True)

    # Clear input and update context
    md = _format_recent_context_markdown(conversation_id)
    return normalized, conversation_id, show_modal, "", f1, f2, f3

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Agent Companion Chatbot")

    user_id = gr.Textbox(label="User ID", value="user_001")

    chatbot = gr.Chatbot(type='messages')
    msg = gr.Textbox(label="Your message", placeholder="Type your message here...")
    send_btn = gr.Button("Send")

    # Recent context panel
    context_md = gr.Markdown(visible=True)

    # Suggested follow-up chips (up to 3)
    with gr.Row():
        follow1 = gr.Button(visible=False)
        follow2 = gr.Button(visible=False)
        follow3 = gr.Button(visible=False)

    # Inline Yes/No buttons (shown below chatbot when a yes/no question is pending)
    with gr.Row(visible=False) as yesno_inline:
        yes_btn = gr.Button("Yes", variant="primary")
        no_btn = gr.Button("No")

    # Modal for Mood emojis
    with gr.Group(visible=False) as mood_modal:
        gr.Markdown("### How are you feeling right now?")
        mood_prompt = gr.Markdown("")
        with gr.Row():
            mood_very_good = gr.Button("😊 very_good")
            mood_good = gr.Button("🙂 good")
            mood_neutral = gr.Button("😐 neutral")
            mood_down = gr.Button("🙁 down")
            mood_sad = gr.Button("😢 sad")
            mood_angry = gr.Button("😠 angry")
            mood_anxious = gr.Button("😰 anxious")

    # State variables
    conversation_id = gr.State(None)

    def send_message(message, history, user_id, conversation_id):
        # Chat
        new_history, new_conversation_id, show_yesno, _, f1, f2, f3 = chat_with_agent(message, history, user_id, conversation_id)
        # Mood modal visibility
        state = companion.memory.get(new_conversation_id) if new_conversation_id else None
        show_mood = gr.update(visible=bool(state and getattr(state, "pending_mood", False)))
        mood_q = state.pending_mood_prompt if state else ""
        # Update modal and context
        return new_history, new_conversation_id, "", _format_recent_context_markdown(new_conversation_id), show_yesno, show_mood, gr.update(value=mood_q), f1, f2, f3

    send_btn.click(
        send_message,
        inputs=[msg, chatbot, user_id, conversation_id],
        outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3]
    )

    def followup_click(btn_text, history, user_id, conversation_id):
        return send_message(btn_text, history, user_id, conversation_id)

    follow1.click(
        followup_click,
        inputs=[follow1, chatbot, user_id, conversation_id],
        outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3],
    )
    follow2.click(
        followup_click,
        inputs=[follow2, chatbot, user_id, conversation_id],
        outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3],
    )
    follow3.click(
        followup_click,
        inputs=[follow3, chatbot, user_id, conversation_id],
        outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3],
    )

    # Handle Yes/No -> auto-send and close modal
    def yes_click(history, user_id, conversation_id):
        state = companion.memory.get(conversation_id)
        if state:
            state.pending_yes_no = False
            state.pending_yes_no_question = None
        return send_message("Yes", history, user_id, conversation_id)

    def no_click(history, user_id, conversation_id):
        state = companion.memory.get(conversation_id)
        if state:
            state.pending_yes_no = False
            state.pending_yes_no_question = None
        return send_message("No", history, user_id, conversation_id)

    yes_btn.click(
        yes_click,
        inputs=[chatbot, user_id, conversation_id],
        outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3]
    )
    no_btn.click(
        no_click,
        inputs=[chatbot, user_id, conversation_id],
        outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3]
    )

    # Mood modal handlers: set current mood and close modal
    def set_mood_and_send(choice: str, history, user_id, conversation_id):
        state = companion.memory.get(conversation_id)
        if state:
            state.pending_mood = False
            state.pending_mood_prompt = None
            # extract label after space if any
            label = choice.split(" ", 1)[-1] if " " in choice else choice
            state.current_mood = label.strip()
        # send the emoji itself as the user's chat input
        emoji = choice.split(" ", 1)[0] if " " in choice else choice
        return send_message(emoji, history, user_id, conversation_id)

    mood_very_good.click(set_mood_and_send, inputs=[gr.State("😊 very_good"), chatbot, user_id, conversation_id], outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3])
    mood_good.click(      set_mood_and_send, inputs=[gr.State("🙂 good"),       chatbot, user_id, conversation_id], outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3])
    mood_neutral.click(   set_mood_and_send, inputs=[gr.State("😐 neutral"),    chatbot, user_id, conversation_id], outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3])
    mood_down.click(      set_mood_and_send, inputs=[gr.State("🙁 down"),       chatbot, user_id, conversation_id], outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3])
    mood_sad.click(       set_mood_and_send, inputs=[gr.State("😢 sad"),        chatbot, user_id, conversation_id], outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3])
    mood_angry.click(     set_mood_and_send, inputs=[gr.State("😠 angry"),      chatbot, user_id, conversation_id], outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3])
    mood_anxious.click(   set_mood_and_send, inputs=[gr.State("😰 anxious"),    chatbot, user_id, conversation_id], outputs=[chatbot, conversation_id, msg, context_md, yesno_inline, mood_modal, mood_prompt, follow1, follow2, follow3])

    # Idle nudge (manual trigger)
    nudge_btn = gr.Button("Check-in (Ask Yes/No)")

    def maybe_nudge(history, conversation_id):
        question = companion.maybe_yes_no_nudge(conversation_id)
        if question:
            state = companion.memory.get(conversation_id)
            if state:
                state.append_assistant(question)
                state.mark_nudge()
                state.pending_yes_no = True
                state.pending_yes_no_question = question
            history = history + [["", question]]
        md = _format_recent_context_markdown(conversation_id)
        # Refresh follow-ups after nudge
        state = companion.memory.get(conversation_id)
        f1 = gr.update(visible=False)
        f2 = gr.update(visible=False)
        f3 = gr.update(visible=False)
        if state and state.suggested_followups:
            items = state.suggested_followups[:3]
            if len(items) > 0:
                f1 = gr.update(value=items[0], visible=True)
            if len(items) > 1:
                f2 = gr.update(value=items[1], visible=True)
            if len(items) > 2:
                f3 = gr.update(value=items[2], visible=True)
        # Show modal when nudged
        show_modal = gr.update(visible=bool(state and state.pending_yes_no))
        return history, md, show_modal, f1, f2, f3

    nudge_btn.click(
        maybe_nudge,
        inputs=[chatbot, conversation_id],
        outputs=[chatbot, context_md, yesno_inline, follow1, follow2, follow3],
    )

    if __name__ == "__main__":
        demo.launch()
