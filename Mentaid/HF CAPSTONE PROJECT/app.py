""" GAIA Enhanced Agent Evaluation Runner"""
import os
import inspect
import gradio as gr
import requests
import pandas as pd
from langchain_core.messages import HumanMessage
from gaia_enhanced_agent import GAIAEnhancedAgent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set HF_TOKEN for Gradio OAuth (required for local development)
hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token



# (Keep Constants as is)
# --- Constants ---
DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"

# --- Basic Agent Definition ---
# ----- THIS IS WERE YOU CAN BUILD WHAT YOU WANT ------


class EnhancedGAIAAgent:
    """Elite GAIA agent with comprehensive multimodal capabilities for 40%+ benchmark performance."""
    def __init__(self):
        print("EnhancedGAIAAgent initialized with comprehensive multimodal capabilities.")
        self.agent = GAIAEnhancedAgent()
        self.question_count = 0

    def __call__(self, question: str) -> str:
        self.question_count += 1
        print(f"Agent received question #{self.question_count} (first 100 chars): {question[:100]}...")
        
        # Add progressive delay between questions to respect rate limits
        if self.question_count > 1:
            import time
            import random
            delay = random.uniform(2, 5)  # Random delay between 2-5 seconds
            print(f"Adding {delay:.1f}s delay to respect rate limits...")
            time.sleep(delay)
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Use the new GAIA enhanced agent
                answer = self.agent.process_question(question)
                
                # Enhanced answer extraction for GAIA format
                final_answer = self._extract_final_answer(answer)
                print(f"Question #{self.question_count} completed successfully")
                return final_answer
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error processing question #{self.question_count} (attempt {attempt + 1}): {error_msg}")
                
                # Check if it's a rate limit error
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    if attempt < max_retries - 1:
                        import time
                        import random
                        wait_time = (2 ** attempt) * 15 + random.uniform(10, 20)
                        print(f"Rate limit detected. Waiting {wait_time:.1f} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "Unable to process due to API rate limits. Please try again later."
                
                # For other errors, try once more with shorter delay
                if attempt < max_retries - 1:
                    import time
                    time.sleep(3)
                    continue
                else:
                    # Return a more user-friendly error message
                    return f"Unable to process question due to technical issues."
    
    def _extract_final_answer(self, answer: str) -> str:
        """Enhanced answer extraction with multiple strategies"""
        from enhanced_agent import AnswerProcessor
        
        processor = AnswerProcessor()
        return processor.extract_and_validate(answer)


def run_and_submit_all( profile: gr.OAuthProfile | None):
    """
    Fetches all questions, runs the BasicAgent on them, submits all answers,
    and displays the results.
    """
    # --- Determine HF Space Runtime URL and Repo URL ---
    space_id = os.getenv("SPACE_ID") # Get the SPACE_ID for sending link to the code

    if profile:
        username= f"{profile.username}"
        print(f"User logged in: {username}")
    else:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    api_url = DEFAULT_API_URL
    questions_url = f"{api_url}/questions"
    submit_url = f"{api_url}/submit"

    # 1. Instantiate Enhanced GAIA Agent with multi-LLM strategy
    try:
        agent = EnhancedGAIAAgent()  # Using enhanced multi-LLM approach
    except Exception as e:
        print(f"Error instantiating enhanced agent: {e}")
        return f"Error initializing enhanced agent: {e}", None
    # In the case of an app running as a hugging Face space, this link points toward your codebase ( usefull for others so please keep it public)
    agent_code = f"https://huggingface.co/spaces/{space_id}/tree/main"
    print(agent_code)

    # 2. Fetch Questions
    print(f"Fetching questions from: {questions_url}")
    try:
        response = requests.get(questions_url, timeout=15)
        response.raise_for_status()
        questions_data = response.json()
        if not questions_data:
             print("Fetched questions list is empty.")
             return "Fetched questions list is empty or invalid format.", None
        print(f"Fetched {len(questions_data)} questions.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching questions: {e}")
        return f"Error fetching questions: {e}", None
    except requests.exceptions.JSONDecodeError as e:
         print(f"Error decoding JSON response from questions endpoint: {e}")
         print(f"Response text: {response.text[:500]}")
         return f"Error decoding server response for questions: {e}", None
    except Exception as e:
        print(f"An unexpected error occurred fetching questions: {e}")
        return f"An unexpected error occurred fetching questions: {e}", None

    # 3. Run your Agent
    results_log = []
    answers_payload = []
    print(f"Running agent on {len(questions_data)} questions...")
    for item in questions_data:
        task_id = item.get("task_id")
        question_text = item.get("question")
        if not task_id or question_text is None:
            print(f"Skipping item with missing task_id or question: {item}")
            continue
        try:
            submitted_answer = agent(question_text)
            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})
            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer})
        except Exception as e:
             print(f"Error running agent on task {task_id}: {e}")
             results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": f"AGENT ERROR: {e}"})

    if not answers_payload:
        print("Agent did not produce any answers to submit.")
        return "Agent did not produce any answers to submit.", pd.DataFrame(results_log)

    # 4. Prepare Submission 
    submission_data = {"username": username.strip(), "agent_code": agent_code, "answers": answers_payload}
    status_update = f"Agent finished. Submitting {len(answers_payload)} answers for user '{username}'..."
    print(status_update)

    # 5. Submit
    print(f"Submitting {len(answers_payload)} answers to: {submit_url}")
    try:
        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        print("Submission successful.")
        results_df = pd.DataFrame(results_log)
        return final_status, results_df
    except requests.exceptions.HTTPError as e:
        error_detail = f"Server responded with status {e.response.status_code}."
        try:
            error_json = e.response.json()
            error_detail += f" Detail: {error_json.get('detail', e.response.text)}"
        except requests.exceptions.JSONDecodeError:
            error_detail += f" Response: {e.response.text[:500]}"
        status_message = f"Submission Failed: {error_detail}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df
    except requests.exceptions.Timeout:
        status_message = "Submission Failed: The request timed out."
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df
    except requests.exceptions.RequestException as e:
        status_message = f"Submission Failed: Network error - {e}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df
    except Exception as e:
        status_message = f"An unexpected error occurred during submission: {e}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df


# --- Build Gradio Interface using Blocks ---
with gr.Blocks() as demo:
    gr.Markdown("# 🚀 Elite GAIA Agent - Multi-LLM Strategy")
    gr.Markdown(
        """
        **🎯 ENHANCED GAIA BENCHMARK AGENT - TARGET: 30%+ SCORE**

        **🧠 Multi-LLM Strategy:**
        - **Primary**: Groq Llama-3.1-70B (Ultra-fast reasoning)
        - **Secondary**: Google Gemini 2.0 Flash (Tool integration)
        - **Fallback**: Mixtral-8x7B (Reliability backup)
        
        **🛠️ Advanced Tool Suite:**
        - 🧮 **Advanced Calculator**: Symbolic math, statistics, calculus
        - 💻 **Code Executor**: Python code execution for complex problems
        - 📊 **Excel Processor**: Data analysis and file processing
        - 🖼️ **Image Analyzer**: Visual content processing
        - 🔍 **Enhanced Search**: Multi-source research with validation
        - 📚 **Academic Search**: ArXiv and scholarly content

        **📋 Setup Instructions:**
        1. **Required API Keys** in your `.env` file:
           - `GROQ_API_KEY` (Primary - Ultra-fast reasoning)
           - `GOOGLE_API_KEY` (Secondary - Tool integration)
           - `TAVILY_API_KEY` (Web search)
           - `HUGGINGFACE_API_TOKEN` (Fallback LLM)
        
        2. **Login**: Use the HuggingFace login button below
        
        3. **Run Evaluation**: Click to test on 20 GAIA benchmark questions

        ---
        **🎯 Performance Optimizations:**
        - **Smart LLM Routing**: Question analysis → Optimal LLM selection
        - **Advanced Tools**: File processing, code execution, symbolic math
        - **Multi-Source Research**: Cross-validation from multiple sources
        - **Enhanced Answer Processing**: Intelligent extraction and formatting
        - **Strategic Rate Limiting**: Provider-specific limits and fallbacks
        
        **⏱️ Expected Runtime**: 10-20 minutes (Groq speed advantage)
        
        **🚀 Key Improvements:**
        - Multi-LLM strategy with intelligent routing
        - Comprehensive tool suite for complex problems
        - Advanced mathematical and computational capabilities
        - Enhanced file processing (Excel, images, PDFs)
        - Strategic question analysis and tool selection
        """
    )

    gr.LoginButton()

    run_button = gr.Button("Run Evaluation & Submit All Answers")

    status_output = gr.Textbox(label="Run Status / Submission Result", lines=5, interactive=False)
    # Removed max_rows=10 from DataFrame constructor
    results_table = gr.DataFrame(label="Questions and Agent Answers", wrap=True)

    run_button.click(
        fn=run_and_submit_all,
        outputs=[status_output, results_table]
    )

if __name__ == "__main__":
    print("\n" + "-"*30 + " App Starting " + "-"*30)
    # Check for SPACE_HOST and SPACE_ID at startup for information
    space_host_startup = os.getenv("SPACE_HOST")
    space_id_startup = os.getenv("SPACE_ID") # Get SPACE_ID at startup

    if space_host_startup:
        print(f"✅ SPACE_HOST found: {space_host_startup}")
        print(f"   Runtime URL should be: https://{space_host_startup}.hf.space")
    else:
        print("ℹ️  SPACE_HOST environment variable not found (running locally?).")

    if space_id_startup: # Print repo URLs if SPACE_ID is found
        print(f"✅ SPACE_ID found: {space_id_startup}")
        print(f"   Repo URL: https://huggingface.co/spaces/{space_id_startup}")
        print(f"   Repo Tree URL: https://huggingface.co/spaces/{space_id_startup}/tree/main")
    else:
        print("ℹ️  SPACE_ID environment variable not found (running locally?). Repo URL cannot be determined.")

    print("-"*(60 + len(" App Starting ")) + "\n")

    print("Launching Gradio Interface for Basic Agent Evaluation...")
    demo.launch(debug=True, share=False)