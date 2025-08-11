---
title: GAIA-Optimized Agent Runner
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.25.2
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_expiration_minutes: 480
---

# GAIA-Optimized Agent Evaluation Runner 🚀

A high-performance AI agent optimized for the GAIA (General AI Assistants) benchmark, targeting 30%+ score performance.

## 🎯 Project Overview

This project implements a sophisticated AI agent using LangGraph that combines multiple tools and reasoning capabilities to tackle complex, real-world questions from the GAIA benchmark.

### 🏆 Target Performance
- **Goal**: 30%+ score on GAIA benchmark
- **Current GAIA Leaderboard Leader**: h2oGPTe (65%)
- **GPT-4 Baseline**: ~15% (original paper)

## 🛠️ Architecture

### Core Components
- **Primary LLM**: Google Gemini 2.0 Flash (optimal for reasoning)
- **Backup LLM**: HuggingFace models
- **Search Tools**: Tavily, Wikipedia, ArXiv
- **Math Tools**: Enhanced calculation and equation solving
- **Framework**: LangGraph for agent orchestration

### Key Features
- ✅ Multi-step reasoning and problem decomposition
- ✅ Cross-referencing multiple information sources
- ✅ Enhanced mathematical computation capabilities
- ✅ Optimized answer formatting for GAIA requirements
- ✅ Robust error handling and fallback mechanisms

## 🚀 Quick Start

### 1. Configure API Keys
Create a `.env` file with:
```env
# Primary LLM (Best performance)
GOOGLE_API_KEY=your_google_api_key_here

# Web Search
TAVILY_API_KEY=your_tavily_api_key_here

# Backup LLM
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
```

### 2. Run the Application
The app will automatically use Google Gemini for optimal GAIA performance.

## 📊 Key Optimizations

### Enhanced Capabilities
- **5 search results** instead of 3 for comprehensive information
- **Advanced mathematical functions** including statistics
- **Cross-referencing** across multiple sources
- **GAIA-specific answer formatting**

### Performance Features
- Multi-step reasoning approach
- Enhanced error handling
- Optimized tool usage strategy
- Improved answer extraction

## 🎯 Expected GAIA Performance: 30%+ 

Ready to achieve top-tier performance on the GAIA benchmark!