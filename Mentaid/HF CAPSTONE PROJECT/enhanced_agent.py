"""Enhanced GAIA Agent - Multi-LLM Strategy with Advanced Tools"""
import os
import time
import random
import re
import asyncio
import tempfile
import io
from typing import Optional, Dict, Any, List
from functools import lru_cache
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.document_loaders import ArxivLoader
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
import logging
import pandas as pd
import numpy as np
import requests
from PIL import Image
import json
import sympy as sp
from scipy import stats
import matplotlib.pyplot as plt

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced Rate Limiter
class SmartRateLimiter:
    def __init__(self, groq_rpm=30, google_rpm=15, hf_rpm=10):
        self.limits = {
            'groq': {'rpm': groq_rpm, 'calls': []},
            'groq-backup': {'rpm': groq_rpm, 'calls': []},
            'google': {'rpm': google_rpm, 'calls': []},
            'hf': {'rpm': hf_rpm, 'calls': []}
        }
    
    def wait_if_needed(self, provider='groq'):
        """Smart rate limiting based on provider"""
        now = time.time()
        provider_data = self.limits[provider]
        
        # Clean old calls
        provider_data['calls'] = [call_time for call_time in provider_data['calls'] 
                                 if now - call_time < 60]
        
        if len(provider_data['calls']) >= provider_data['rpm']:
            wait_time = 60 - (now - provider_data['calls'][0]) + random.uniform(1, 3)
            logger.info(f"{provider.upper()} rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            now = time.time()
            provider_data['calls'] = [call_time for call_time in provider_data['calls'] 
                                     if now - call_time < 60]
        
        provider_data['calls'].append(now)

# Global rate limiter
rate_limiter = SmartRateLimiter()

# Question Analysis System
class QuestionAnalyzer:
    def __init__(self):
        self.patterns = {
            'mathematical': r'calculate|compute|solve|equation|number|sum|product|divide|multiply|\d+',
            'factual': r'who|what|when|where|which|name|identify',
            'multimodal': r'image|video|file|excel|pdf|attachment|picture|chart|graph',
            'reasoning': r'analyze|compare|explain|why|how|reason|logic|deduce',
            'temporal': r'date|time|year|month|day|before|after|during',
            'quantitative': r'how many|count|total|sum|average|percentage'
        }
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        
        # Classify question type
        question_type = 'general'
        max_matches = 0
        
        for qtype, pattern in self.patterns.items():
            matches = len(re.findall(pattern, question_lower))
            if matches > max_matches:
                max_matches = matches
                question_type = qtype
        
        # Assess complexity
        complexity = 'low'
        if len(question.split()) > 50:
            complexity = 'high'
        elif len(question.split()) > 25:
            complexity = 'medium'
        
        # Predict required tools
        required_tools = []
        if re.search(r'search|find|look up', question_lower):
            required_tools.append('web_search')
        if re.search(r'calculate|math|compute', question_lower):
            required_tools.append('calculator')
        if re.search(r'image|picture|chart', question_lower):
            required_tools.append('image_processor')
        if re.search(r'excel|csv|data', question_lower):
            required_tools.append('excel_processor')
        
        return {
            'type': question_type,
            'complexity': complexity,
            'required_tools': required_tools,
            'word_count': len(question.split()),
            'has_urls': bool(re.search(r'http[s]?://|www\.', question))
        }

# Smart LLM Router
class SmartLLMRouter:
    def __init__(self):
        self.groq_llm = None
        self.groq_backup = None  # Backup Groq model
        self.gemini_llm = None
        self.hf_llm = None
        self.analyzer = QuestionAnalyzer()
        self.setup_llms()
    
    def setup_llms(self):
        """Initialize all available LLMs"""
        try:
            # Groq - Primary for reasoning (using latest working model)
            if os.getenv("GROQ_API_KEY"):
                self.groq_llm = ChatGroq(
                    model="llama-3.3-70b-versatile",  # Latest working 70B model
                    temperature=0,
                    max_tokens=4096,
                    groq_api_key=os.getenv("GROQ_API_KEY")
                )
                logger.info("Groq LLM (llama-3.3-70b-versatile) initialized successfully")
                
                # Also initialize backup Groq model
                self.groq_backup = ChatGroq(
                    model="llama-3.1-8b-instant",  # Fast backup model
                    temperature=0,
                    max_tokens=4096,
                    groq_api_key=os.getenv("GROQ_API_KEY")
                )
                logger.info("Groq backup LLM (llama-3.1-8b-instant) initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Groq LLM: {e}")
        
        try:
            # Google Gemini - Secondary for tool integration (using stable model)
            if os.getenv("GOOGLE_API_KEY"):
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",  # More stable, higher quota
                    temperature=0,
                    max_tokens=4096
                )
                logger.info("Google Gemini LLM (gemini-1.5-flash) initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Google LLM: {e}")
        
        try:
            # HuggingFace - Fallback
            if os.getenv("HUGGINGFACE_API_TOKEN"):
                self.hf_llm = ChatHuggingFace(
                    llm=HuggingFaceEndpoint(
                        repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                        temperature=0,
                        max_new_tokens=2048,
                        huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN")
                    ),
                )
                logger.info("HuggingFace LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize HuggingFace LLM: {e}")
    
    def select_best_llm(self, question: str):
        """Select the best LLM based on question analysis"""
        analysis = self.analyzer.analyze_question(question)
        
        # Strategy: Groq for reasoning, Gemini for tools, HF for fallback
        if analysis['type'] in ['mathematical', 'reasoning'] and self.groq_llm:
            return self.groq_llm, 'groq'
        elif analysis['complexity'] == 'high' and len(analysis['required_tools']) > 2 and self.gemini_llm:
            return self.gemini_llm, 'google'
        elif self.groq_llm:
            return self.groq_llm, 'groq'
        elif self.gemini_llm:
            return self.gemini_llm, 'google'
        elif self.hf_llm:
            return self.hf_llm, 'hf'
        else:
            raise ValueError("No LLM available")
    
    def invoke_with_smart_fallback(self, messages, max_retries=3):
        """Invoke with intelligent fallback strategy"""
        question = messages[-1].content if messages else ""
        
        # Try primary LLM selection
        try:
            primary_llm, provider = self.select_best_llm(question)
            for attempt in range(max_retries):
                try:
                    rate_limiter.wait_if_needed(provider)
                    logger.info(f"Using {provider.upper()} LLM (attempt {attempt + 1})")
                    result = primary_llm.invoke(messages)
                    logger.info(f"{provider.upper()} LLM call successful")
                    return result
                except Exception as e:
                    logger.warning(f"{provider.upper()} attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt + random.uniform(1, 3))
        except Exception as e:
            logger.warning(f"Primary LLM selection failed: {e}")
        
        # Fallback chain: Groq -> Groq Backup -> Gemini -> HF
        fallback_order = [
            (self.groq_llm, 'groq'),
            (self.groq_backup, 'groq-backup'),
            (self.gemini_llm, 'google'),
            (self.hf_llm, 'hf')
        ]
        
        for llm, provider in fallback_order:
            if llm:
                try:
                    rate_limiter.wait_if_needed(provider)
                    logger.info(f"Fallback to {provider.upper()} LLM")
                    result = llm.invoke(messages)
                    logger.info(f"Fallback {provider.upper()} successful")
                    return result
                except Exception as e:
                    logger.warning(f"Fallback {provider.upper()} failed: {e}")
                    time.sleep(2)
        
        raise Exception("All LLM attempts failed")

# Advanced Tools
@tool
def advanced_calculator(expression: str) -> str:
    """Advanced mathematical calculator with support for complex operations, statistics, and symbolic math.
    
    Args:
        expression: Mathematical expression (e.g., "sqrt(16)", "factorial(5)", "integrate(x**2, x)", "solve(x**2 - 4, x)")
    """
    try:
        import math
        import statistics
        import sympy as sp
        from scipy import stats
        
        # Enhanced mathematical environment
        math_env = {
            # Basic math
            **{k: v for k, v in math.__dict__.items() if not k.startswith("__")},
            # Statistics
            'mean': statistics.mean, 'median': statistics.median, 'mode': statistics.mode,
            'stdev': statistics.stdev, 'variance': statistics.variance,
            # Scipy stats
            'norm': stats.norm, 'binom': stats.binom, 'poisson': stats.poisson,
            # Sympy functions
            'symbols': sp.symbols, 'solve': sp.solve, 'integrate': sp.integrate,
            'diff': sp.diff, 'limit': sp.limit, 'series': sp.series,
            'simplify': sp.simplify, 'expand': sp.expand, 'factor': sp.factor,
            # Built-ins
            'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum,
            'len': len, 'range': range, 'pow': pow, 'divmod': divmod
        }
        
        # Handle symbolic expressions
        if any(op in expression for op in ['solve', 'integrate', 'diff', 'limit']):
            # Symbolic math
            result = eval(expression, {"__builtins__": {}}, math_env)
            return str(result)
        else:
            # Numerical calculation
            result = eval(expression, {"__builtins__": {}}, math_env)
            return str(result)
            
    except Exception as e:
        return f"Calculation error: {str(e)}"

@tool
def code_executor(code: str, language: str = "python") -> str:
    """Execute Python code safely for computational problems.
    
    Args:
        code: Python code to execute
        language: Programming language (currently only 'python' supported)
    """
    try:
        if language.lower() != "python":
            return "Only Python code execution is currently supported."
        
        # Create safe execution environment
        safe_globals = {
            '__builtins__': {
                'print': print, 'len': len, 'range': range, 'enumerate': enumerate,
                'sum': sum, 'min': min, 'max': max, 'abs': abs, 'round': round,
                'sorted': sorted, 'reversed': reversed, 'zip': zip
            },
            'math': __import__('math'),
            'statistics': __import__('statistics'),
            'random': __import__('random'),
            'datetime': __import__('datetime'),
            'json': __import__('json'),
            'pandas': __import__('pandas'),
            'numpy': __import__('numpy')
        }
        
        # Capture output
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            exec(code, safe_globals)
            output = captured_output.getvalue()
            return output if output else "Code executed successfully (no output)"
        finally:
            sys.stdout = old_stdout
            
    except Exception as e:
        return f"Code execution error: {str(e)}"

@tool
def process_excel_file(file_url: str) -> str:
    """Download and analyze Excel files from URLs.
    
    Args:
        file_url: URL of the Excel file to process
    """
    try:
        # Download file
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        # Read Excel file
        try:
            df = pd.read_excel(tmp_path)
        except:
            # Try with different engines
            df = pd.read_excel(tmp_path, engine='openpyxl')
        
        # Basic analysis
        analysis = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'head': df.head().to_dict(),
            'summary': df.describe().to_dict() if df.select_dtypes(include=[np.number]).shape[1] > 0 else {}
        }
        
        # Clean up
        os.unlink(tmp_path)
        
        return f"Excel Analysis:\nShape: {analysis['shape']}\nColumns: {analysis['columns']}\nFirst 5 rows: {analysis['head']}\nSummary: {analysis['summary']}"
        
    except Exception as e:
        return f"Excel processing error: {str(e)}"

@tool
def process_image(image_url: str) -> str:
    """Analyze images from URLs (basic image processing).
    
    Args:
        image_url: URL of the image to analyze
    """
    try:
        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Open image
        image = Image.open(io.BytesIO(response.content))
        
        # Basic analysis
        analysis = {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
        }
        
        return f"Image Analysis:\nFormat: {analysis['format']}\nSize: {analysis['size']}\nMode: {analysis['mode']}\nHas transparency: {analysis['has_transparency']}"
        
    except Exception as e:
        return f"Image processing error: {str(e)}"

@tool
def enhanced_web_search(query: str, domain: str = None, max_results: int = 5) -> str:
    """Enhanced web search with domain filtering and better result processing.
    
    Args:
        query: Search query
        domain: Optional domain to restrict search to
        max_results: Maximum number of results to return
    """
    try:
        time.sleep(0.5)  # Rate limiting
        
        # Modify query for domain filtering
        if domain:
            query = f"site:{domain} {query}"
        
        search_tool = TavilySearchResults(max_results=max_results, search_depth="advanced")
        search_docs = search_tool.invoke(query)
        
        if isinstance(search_docs, list) and search_docs:
            formatted_results = []
            for i, doc in enumerate(search_docs[:max_results], 1):
                formatted_results.append(
                    f"Result {i}:\nTitle: {doc.get('title', 'N/A')}\n"
                    f"URL: {doc.get('url', 'N/A')}\n"
                    f"Content: {doc.get('content', 'N/A')[:500]}...\n"
                )
            
            return "\n---\n".join(formatted_results)
        else:
            return f"No web search results found for query: {query}"
            
    except Exception as e:
        logger.warning(f"Enhanced web search failed for query '{query}': {e}")
        return f"Web search temporarily unavailable. Error: {str(e)}"

@tool
def academic_search(query: str, max_results: int = 3) -> str:
    """Enhanced academic search combining ArXiv and other sources.
    
    Args:
        query: Academic search query
        max_results: Maximum number of results
    """
    try:
        time.sleep(0.5)
        
        # ArXiv search
        arxiv_docs = ArxivLoader(query=query, load_max_docs=max_results).load()
        
        results = []
        if arxiv_docs:
            for doc in arxiv_docs:
                results.append(
                    f"ArXiv Paper:\n"
                    f"Title: {doc.metadata.get('Title', 'N/A')}\n"
                    f"Authors: {doc.metadata.get('Authors', 'N/A')}\n"
                    f"Published: {doc.metadata.get('Published', 'N/A')}\n"
                    f"Summary: {doc.page_content[:800]}...\n"
                )
        
        if results:
            return "\n---\n".join(results)
        else:
            return f"No academic papers found for: {query}"
            
    except Exception as e:
        logger.warning(f"Academic search failed for query '{query}': {e}")
        return f"Academic search temporarily unavailable for query: {query}"

# Keep existing basic tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b

@tool
def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia for information."""
    try:
        time.sleep(0.3)
        search_docs = WikipediaLoader(query=query, load_max_docs=2).load()
        if search_docs:
            formatted_docs = "\n\n---\n\n".join([
                f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content[:2000]}\n</Document>'
                for doc in search_docs
            ])
            return formatted_docs
        else:
            return f"No Wikipedia articles found for: {query}"
    except Exception as e:
        logger.warning(f"Wikipedia search failed: {e}")
        return f"Wikipedia search temporarily unavailable for query: {query}"

# All available tools
tools = [
    # Basic math
    multiply, add, subtract, divide,
    # Advanced tools
    advanced_calculator, code_executor,
    # File processing
    process_excel_file, process_image,
    # Search tools
    enhanced_web_search, academic_search, wiki_search,
]

# Enhanced Answer Processor
class AnswerProcessor:
    def __init__(self):
        self.answer_patterns = [
            r"FINAL ANSWER:\s*(.+?)(?:\n|$)",
            r"Answer:\s*(.+?)(?:\n|$)",
            r"The answer is:\s*(.+?)(?:\n|$)",
            r"Result:\s*(.+?)(?:\n|$)",
        ]
    
    def extract_and_validate(self, response: str, question_type: str = 'general') -> str:
        """Extract and validate the final answer"""
        if not response or not isinstance(response, str):
            return "No answer provided"
        
        # Try pattern matching first
        for pattern in self.answer_patterns:
            match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
            if match:
                answer = match.group(1).strip()
                return self.format_answer(answer, question_type)
        
        # Fallback: extract last substantive line
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        if lines:
            for line in reversed(lines):
                if not line.endswith("?") and len(line) > 3:
                    return self.format_answer(line, question_type)
            return self.format_answer(lines[-1], question_type)
        
        return self.format_answer(response.strip()[:200], question_type)
    
    def format_answer(self, answer: str, question_type: str) -> str:
        """Format answer based on question type"""
        # Clean up formatting
        answer = re.sub(r'\*+', '', answer)  # Remove markdown
        answer = re.sub(r'#+', '', answer)   # Remove headers
        answer = answer.strip()
        
        # Type-specific formatting
        if question_type == 'mathematical':
            # Extract numbers if present
            numbers = re.findall(r'-?\d+\.?\d*', answer)
            if numbers:
                return numbers[-1]  # Return last number found
        
        return answer

# Load system prompt
with open("d:/Projects/AI AGENTS/HF CAPSTONE PROJECT/system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

sys_msg = SystemMessage(content=system_prompt)

# Enhanced build_graph function
def build_enhanced_graph():
    """Build enhanced graph with multi-LLM strategy"""
    
    # Initialize smart LLM router
    llm_router = SmartLLMRouter()
    answer_processor = AnswerProcessor()
    
    # Get primary LLM for tool binding
    primary_llm = None
    if llm_router.groq_llm:
        primary_llm = llm_router.groq_llm
    elif llm_router.gemini_llm:
        primary_llm = llm_router.gemini_llm
    elif llm_router.hf_llm:
        primary_llm = llm_router.hf_llm
    else:
        raise ValueError("No LLM available. Check your API keys.")
    
    llm_with_tools = primary_llm.bind_tools(tools)
    
    def enhanced_assistant(state: MessagesState):
        """Enhanced assistant with smart LLM routing"""
        try:
            result = llm_router.invoke_with_smart_fallback(state["messages"])
            return {"messages": [result]}
        except Exception as e:
            logger.error(f"All LLM attempts failed: {e}")
            error_msg = HumanMessage(content=f"I apologize, but I'm experiencing technical difficulties. Please try again.")
            return {"messages": [error_msg]}
    
    def retriever(state: MessagesState):
        """Enhanced retriever with system message"""
        return {"messages": [sys_msg] + state["messages"]}
    
    # Build graph
    builder = StateGraph(MessagesState)
    builder.add_node("retriever", retriever)
    builder.add_node("assistant", enhanced_assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    
    return builder.compile()

# Test function
if __name__ == "__main__":
    print("🚀 Testing Enhanced GAIA Agent with Multi-LLM Strategy")
    print("=" * 60)
    
    # Test question
    test_question = "What is the square root of 144 plus 5 factorial?"
    
    try:
        graph = build_enhanced_graph()
        messages = [HumanMessage(content=test_question)]
        result = graph.invoke({"messages": messages})
        
        answer = result['messages'][-1].content
        print(f"Question: {test_question}")
        print(f"Answer: {answer}")
        
        # Test answer processing
        processor = AnswerProcessor()
        final_answer = processor.extract_and_validate(answer, 'mathematical')
        print(f"Processed Answer: {final_answer}")
        
    except Exception as e:
        print(f"Test failed: {e}")