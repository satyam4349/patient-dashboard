---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary
This repository contains a comprehensive mental health platform with multiple components: a FastAPI backend, a Next.js frontend, and an AI agent system built with LangChain. The project focuses on mental health analysis and patient management with advanced AI capabilities.

## Repository Structure
- **Backend**: FastAPI application with authentication, patient management, and AI agent integration
- **frontend-app**: Next.js web application with TypeScript and Tailwind CSS
- **HF CAPSTONE PROJECT**: Hugging Face AI agent implementation using LangChain
- **other testing stuff**: Prototype implementations and model testing
- **Others**: Datasets, notebooks, and additional resources

## Projects

### Backend
**Configuration File**: requirements.txt

#### Language & Runtime
**Language**: Python
**Version**: 3.11
**Framework**: FastAPI
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- fastapi>=0.111,<1
- uvicorn[standard]>=0.30,<1
- supabase>=2.4,<3
- langchain>=0.1.0,<0.3
- torch>=2.2,<3
- transformers>=4.41,<5

#### Build & Installation
```bash
pip install -r requirements.txt
python main.py
```

#### Docker
**Dockerfile**: Backend/Dockerfile
**Image**: Python 3.11-slim
**Configuration**: docker-compose.yml with API and optional Nginx services

#### Testing
**Framework**: pytest
**Test Location**: Backend/test.py
**Run Command**:
```bash
pytest
```

### frontend-app
**Configuration File**: package.json

#### Language & Runtime
**Language**: TypeScript
**Version**: TypeScript 5
**Framework**: Next.js 15.4.6
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- next: 15.4.6
- react: 19.1.0
- react-dom: 19.1.0
- axios: ^1.11.0
- recharts: ^3.1.2

**Development Dependencies**:
- typescript: ^5
- tailwindcss: ^4
- eslint: ^9

#### Build & Installation
```bash
npm install
npm run build
npm start
```

### HF CAPSTONE PROJECT
**Configuration File**: requirements.txt

#### Language & Runtime
**Language**: Python
**Version**: 3.11
**Framework**: Gradio, LangChain
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- gradio[oauth]>=5.35.0
- langchain>=0.1.0
- langchain-community>=0.0.20
- langchain-google-genai>=1.0.0
- langchain-groq>=0.1.0
- huggingface_hub>=0.19.0

#### Build & Installation
```bash
pip install -r requirements.txt
python app.py
```

#### Testing
**Test Files**: test_agent.py, test_enhanced_agent.py, test_gaia_capabilities.py
**Run Command**:
```bash
python test_agent.py
```

### other testing stuff/Prototype
**Configuration File**: description.txt

#### Language & Runtime
**Language**: Python
**Framework**: Various ML/NLP libraries
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- scikit-learn
- transformers
- torch
- nltk

#### Key Files
- nlp_transformer_1_2.py
- svm_1_2.py
- lexical_complexity_analyzer.py
- semantic_coherence.py