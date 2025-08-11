"""LangGraph Agent - Optimized for GAIA Benchmark with Rate Limiting & Fallback"""
import os
import time
import random
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.document_loaders import ArxivLoader
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting configuration
class RateLimiter:
    def __init__(self, calls_per_minute: int = 8):  # Conservative limit for free tier
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if we're approaching rate limits"""
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        if len(self.calls) >= self.calls_per_minute:
            # Wait until the oldest call is more than 1 minute old
            wait_time = 60 - (now - self.calls[0]) + random.uniform(1, 3)  # Add jitter
            logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            # Clean up old calls again
            now = time.time()
            self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        self.calls.append(now)

# Global rate limiter
rate_limiter = RateLimiter()

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: first int
        b: second int
    """
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add two numbers.
    
    Args:
        a: first int
        b: second int
    """
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers.
    
    Args:
        a: first int
        b: second int
    """
    return a - b

@tool
def divide(a: int, b: int) -> int:
    """Divide two numbers.
    
    Args:
        a: first int
        b: second int
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

@tool
def modulus(a: int, b: int) -> int:
    """Get the modulus of two numbers.
    
    Args:
        a: first int
        b: second int
    """
    return a % b

@tool
def calculate(expression: str) -> str:
    """Safely evaluate mathematical expressions with enhanced capabilities.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4", "sqrt(16)", "2**3", "factorial(5)")
    """
    try:
        import math
        import statistics
        
        # Allow comprehensive mathematical operations
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({
            "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
            "len": len, "range": range, "enumerate": enumerate,
            "mean": statistics.mean, "median": statistics.median, 
            "mode": statistics.mode, "stdev": statistics.stdev,
            "factorial": math.factorial, "gcd": math.gcd,
            "pow": pow, "divmod": divmod
        })
        
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"

@tool
def solve_equation(equation: str) -> str:
    """Solve simple algebraic equations and return the solution.
    
    Args:
        equation: Equation to solve (e.g., "2*x + 5 = 15", "x**2 - 4 = 0")
    """
    try:
        # Simple equation solver for basic cases
        if "=" in equation:
            left, right = equation.split("=")
            left, right = left.strip(), right.strip()
            
            # For simple linear equations like "2*x + 5 = 15"
            if "x" in left and right.isdigit():
                # This is a simplified solver - for demo purposes
                return f"Equation solving requires more advanced symbolic math. Try using calculate() for specific values."
            else:
                return f"Equation format not supported. Use calculate() for numerical expressions."
        else:
            return "Please provide an equation with '=' sign."
    except Exception as e:
        return f"Equation solving error: {str(e)}"

@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia for a query and return maximum 2 results.
    
    Args:
        query: The search query."""
    try:
        time.sleep(0.3)  # Brief delay
        search_docs = WikipediaLoader(query=query, load_max_docs=2).load()
        if search_docs:
            formatted_search_docs = "\n\n---\n\n".join(
                [
                    f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content[:2000]}\n</Document>'
                    for doc in search_docs
                ])
            return formatted_search_docs
        else:
            return f"No Wikipedia articles found for: {query}"
    except Exception as e:
        logger.warning(f"Wikipedia search failed for query '{query}': {e}")
        return f"Wikipedia search temporarily unavailable for query: {query}"

@tool
def web_search(query: str) -> str:
    """Search Tavily for a query and return maximum 5 results with enhanced content.
    
    Args:
        query: The search query."""
    try:
        # Add small delay to avoid overwhelming the API
        time.sleep(0.5)
        search_docs = TavilySearchResults(max_results=5, search_depth="advanced").invoke(query)
        if isinstance(search_docs, list) and search_docs:
            formatted_search_docs = "\n\n---\n\n".join(
                [
                    f'<Document source="{doc.get("url", "")}" title="{doc.get("title", "")}">\n{doc.get("content", "")}\n</Document>'
                    for doc in search_docs[:3]  # Limit to top 3 results to reduce token usage
                ])
            return formatted_search_docs
        else:
            return f"No web search results found for query: {query}"
    except Exception as e:
        logger.warning(f"Web search failed for query '{query}': {e}")
        return f"Web search temporarily unavailable. Try rephrasing your query or using other tools."

@tool
def arxiv_search(query: str) -> str:
    """Search Arxiv for a query and return maximum 3 results with enhanced metadata.
    
    Args:
        query: The search query."""
    try:
        time.sleep(0.5)  # Brief delay
        search_docs = ArxivLoader(query=query, load_max_docs=3).load()
        if search_docs:
            formatted_search_docs = "\n\n---\n\n".join(
                [
                    f'<Document source="{doc.metadata["source"]}" title="{doc.metadata.get("Title", "")}" authors="{doc.metadata.get("Authors", "")}" published="{doc.metadata.get("Published", "")}">\n{doc.page_content[:1200]}\n</Document>'
                    for doc in search_docs
                ])
            return formatted_search_docs
        else:
            return f"No ArXiv papers found for: {query}"
    except Exception as e:
        logger.warning(f"ArXiv search failed for query '{query}': {e}")
        return f"ArXiv search temporarily unavailable for query: {query}"



# load the system prompt from the file
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# System message
sys_msg = SystemMessage(content=system_prompt)

# Removed Supabase dependency for quick deployment
# Using only HF + Tavily APIs



tools = [
    multiply,
    add,
    subtract,
    divide,
    modulus,
    calculate,
    solve_equation,
    wiki_search,
    web_search,
    arxiv_search,
]

# Enhanced LLM with fallback and rate limiting
class EnhancedLLM:
    def __init__(self):
        self.google_llm = None
        self.hf_llm = None
        self.setup_llms()
    
    def setup_llms(self):
        """Setup both Google and HuggingFace LLMs"""
        try:
            # Google Gemini - Primary LLM
            self.google_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp", 
                temperature=0,
                max_tokens=4096
            )
            logger.info("Google Gemini LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Google LLM: {e}")
        
        try:
            # HuggingFace - Fallback LLM (using a better model)
            self.hf_llm = ChatHuggingFace(
                llm=HuggingFaceEndpoint(
                    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",  # Better model for reasoning
                    temperature=0,
                    max_new_tokens=2048,
                    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN")
                ),
            )
            logger.info("HuggingFace LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize HuggingFace LLM: {e}")
            # Fallback to a simpler model if Mixtral fails
            try:
                self.hf_llm = ChatHuggingFace(
                    llm=HuggingFaceEndpoint(
                        repo_id="microsoft/DialoGPT-medium",
                        temperature=0,
                        max_new_tokens=1024,
                        huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN")
                    ),
                )
                logger.info("Fallback HuggingFace LLM initialized")
            except Exception as e2:
                logger.error(f"Failed to initialize fallback HF LLM: {e2}")
    
    def invoke_with_fallback(self, messages, max_retries=3):
        """Invoke LLM with fallback and retry logic"""
        last_error = None
        
        # Try Google first (if available)
        if self.google_llm:
            for attempt in range(max_retries):
                try:
                    rate_limiter.wait_if_needed()  # Respect rate limits
                    logger.info(f"Attempting Google LLM (attempt {attempt + 1})")
                    result = self.google_llm.invoke(messages)
                    logger.info("Google LLM call successful")
                    return result
                except Exception as e:
                    last_error = e
                    logger.warning(f"Google LLM attempt {attempt + 1} failed: {e}")
                    if "429" in str(e) or "quota" in str(e).lower():
                        # Rate limit hit, wait longer
                        wait_time = (2 ** attempt) * 10 + random.uniform(5, 15)
                        logger.info(f"Rate limit detected, waiting {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                    elif attempt < max_retries - 1:
                        # Other error, shorter wait
                        time.sleep(2 ** attempt + random.uniform(1, 3))
        
        # Fallback to HuggingFace
        if self.hf_llm:
            logger.info("Falling back to HuggingFace LLM")
            for attempt in range(max_retries):
                try:
                    time.sleep(1)  # Brief pause before fallback
                    result = self.hf_llm.invoke(messages)
                    logger.info("HuggingFace LLM call successful")
                    return result
                except Exception as e:
                    last_error = e
                    logger.warning(f"HuggingFace LLM attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt + random.uniform(1, 2))
        
        # If all fails, raise the last error
        raise Exception(f"All LLM attempts failed. Last error: {last_error}")

# Build graph function
def build_graph(provider: str = "hybrid"):
    """Build the graph with enhanced LLM fallback and rate limiting"""
    
    if provider == "hybrid":
        # Use enhanced LLM with fallback
        enhanced_llm = EnhancedLLM()
        
        # Bind tools to primary LLM (Google if available, otherwise HF)
        primary_llm = enhanced_llm.google_llm if enhanced_llm.google_llm else enhanced_llm.hf_llm
        if not primary_llm:
            raise ValueError("No LLM available. Check your API keys.")
        
        llm_with_tools = primary_llm.bind_tools(tools)
        
        # Enhanced assistant node with fallback
        def assistant(state: MessagesState):
            """Enhanced assistant node with fallback logic"""
            try:
                result = enhanced_llm.invoke_with_fallback(state["messages"])
                return {"messages": [result]}
            except Exception as e:
                logger.error(f"All LLM attempts failed: {e}")
                # Return error message as fallback
                error_msg = HumanMessage(content=f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)[:200]}...")
                return {"messages": [error_msg]}
    
    elif provider == "google":
        # Google only (original behavior)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", 
            temperature=0,
            max_tokens=4096
        )
        llm_with_tools = llm.bind_tools(tools)
        
        def assistant(state: MessagesState):
            """Assistant node with rate limiting"""
            rate_limiter.wait_if_needed()
            return {"messages": [llm_with_tools.invoke(state["messages"])]}
    
    elif provider == "huggingface":
        # HuggingFace only
        llm = ChatHuggingFace(
            llm=HuggingFaceEndpoint(
                repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                temperature=0,
                max_new_tokens=2048,
                huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN")
            ),
        )
        llm_with_tools = llm.bind_tools(tools)
        
        def assistant(state: MessagesState):
            """Assistant node"""
            return {"messages": [llm_with_tools.invoke(state["messages"])]}
    
    else:
        raise ValueError("Invalid provider. Choose 'hybrid', 'google', or 'huggingface'.")
    
    def retriever(state: MessagesState):
        """Simple system message injection - no vector search needed"""
        return {"messages": [sys_msg] + state["messages"]}

    builder = StateGraph(MessagesState)
    builder.add_node("retriever", retriever)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    # Compile graph
    return builder.compile()

# test
if __name__ == "__main__":
    question = "When was a picture of St. Thomas Aquinas first added to the Wikipedia page on the Principle of double effect?"
    # Build the graph with hybrid provider for best performance and reliability
    graph = build_graph(provider="hybrid")
    # Run the graph
    messages = [HumanMessage(content=question)]
    try:
        messages = graph.invoke({"messages": messages})
        for m in messages["messages"]:
            m.pretty_print()
    except Exception as e:
        print(f"Test failed: {e}")
