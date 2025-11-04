<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.6
-->

# Abhikarta LLM - Requirements Document

**Version:** 3.1.6  
**Date:** November 4, 2025  
**Status:** Production Ready

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Python Requirements](#python-requirements)
3. [Core Dependencies](#core-dependencies)
4. [Optional Dependencies](#optional-dependencies)
5. [Provider Requirements](#provider-requirements)
6. [Multimodal Requirements](#multimodal-requirements)
7. [Installation Instructions](#installation-instructions)
8. [Configuration Requirements](#configuration-requirements)
9. [Platform Support](#platform-support)
10. [Security Requirements](#security-requirements)

---

## System Requirements

### Minimum Hardware
- **CPU:** 2+ cores recommended
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk Space:** 100 MB for package, additional space for models (if using local providers)
- **Network:** Internet connection required for cloud providers

### Recommended Hardware
- **CPU:** 4+ cores for optimal performance
- **RAM:** 16 GB for document processing and multimodal tasks
- **Disk Space:** 10+ GB for local models (Ollama, Meta)
- **GPU:** Optional, but recommended for local model inference

---

## Python Requirements

### Python Version

**Required:** Python 3.8 or higher  
**Recommended:** Python 3.10 or higher  
**Tested On:** Python 3.8, 3.9, 3.10, 3.11, 3.12

```bash
# Check Python version
python3 --version

# Should output: Python 3.8.x or higher
```

### Python Environment

**Options:**
1. System Python (simplest)
2. Virtual Environment (recommended)
3. Conda Environment (for data science)
4. Docker Container (for production)

**Virtual Environment Setup:**
```bash
# Create virtual environment
python3 -m venv abhikarta-env

# Activate (Linux/Mac)
source abhikarta-env/bin/activate

# Activate (Windows)
abhikarta-env\Scripts\activate

# Install package
pip install -e .
```

---

## Core Dependencies

### Required (Included)

These are built-in Python modules - no installation needed:

```
base64              # Multimodal encoding
json                # JSON parsing
csv                 # CSV parsing
mimetypes           # MIME type detection
pathlib             # File path handling
dataclasses         # Data structures
enum                # Enumerations
typing              # Type hints
os                  # OS operations
sys                 # System operations
```

### Installation

```bash
# Basic installation (no external dependencies required)
pip install -e .

# The package works immediately with the mock provider
python3 -c "from llm.abstraction.facade import UnifiedLLMFacade; print('✅ Working')"
```

---

## Optional Dependencies

### For Provider Support

#### OpenAI
```bash
pip install openai>=1.0.0
```
**Required for:**
- GPT-3.5, GPT-4 models
- GPT-4 Vision
- Whisper (audio transcription)
- DALL-E (image generation)

#### Anthropic
```bash
pip install anthropic>=0.7.0
```
**Required for:**
- Claude 3 Opus, Sonnet, Haiku
- Claude 3 Vision capabilities

#### Google
```bash
pip install google-generativeai>=0.3.0
```
**Required for:**
- Gemini Pro, Gemini Ultra
- Gemini Pro Vision
- Google Speech-to-Text

#### AWS Bedrock
```bash
pip install boto3>=1.28.0
pip install botocore>=1.31.0
```
**Required for:**
- Claude on AWS Bedrock
- Llama on AWS Bedrock
- Amazon Titan models

#### Cohere
```bash
pip install cohere>=4.0.0
```
**Required for:**
- Command, Command-R models

#### HuggingFace
```bash
pip install huggingface-hub>=0.16.0
pip install transformers>=4.30.0  # Optional, for local inference
```
**Required for:**
- HuggingFace Inference API
- 100,000+ community models

#### Groq
```bash
pip install groq>=0.4.0
```
**Required for:**
- Ultra-fast Mixtral, Llama inference

#### Mistral
```bash
pip install mistralai>=0.0.7
```
**Required for:**
- Mistral 7B, Mixtral 8x7B models

#### Together
```bash
pip install together>=0.2.0
```
**Required for:**
- 50+ open source models

#### Replicate
```bash
pip install replicate>=0.15.0
```
**Required for:**
- Replicate models
- Stable Diffusion, Llama, etc.

#### Ollama (Local)
```bash
# Install Ollama (not a Python package)
# Linux/Mac
curl https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai

# Pull models
ollama pull llama2
ollama pull mistral
ollama pull llava  # Vision model
```

### Quick Install - All Providers
```bash
pip install openai anthropic google-generativeai boto3 \
    cohere huggingface-hub groq mistralai together replicate
```

---

## Multimodal Requirements

### Document Parsing

#### PDF Support
```bash
pip install PyPDF2>=3.0.0
```
**Provides:**
- PDF text extraction
- Page counting
- Metadata extraction

**Alternative (more features):**
```bash
pip install pdfplumber>=0.9.0  # Better table extraction
pip install PyMuPDF>=1.23.0    # Faster, more features
```

#### DOCX Support
```bash
pip install python-docx>=0.8.11
```
**Provides:**
- Word document parsing
- Paragraph extraction
- Formatting preservation

#### Excel Support
```bash
pip install openpyxl>=3.1.0
```
**Provides:**
- Excel spreadsheet parsing (.xlsx)
- Multiple sheet support
- Cell value extraction

**Alternative:**
```bash
pip install xlrd>=2.0.0  # For older .xls files
```

#### HTML Support
```bash
pip install beautifulsoup4>=4.12.0
pip install lxml>=4.9.0  # XML parser (faster)
```
**Provides:**
- HTML text extraction
- Web scraping
- XML parsing

#### PowerPoint Support
```bash
pip install python-pptx>=0.6.21
```
**Provides:**
- PowerPoint parsing
- Slide text extraction

### Image Processing

```bash
pip install Pillow>=10.0.0
```
**Provides:**
- Image loading and manipulation
- Format conversion
- Image resizing

**Optional (advanced):**
```bash
pip install opencv-python>=4.8.0  # Computer vision
pip install numpy>=1.24.0         # Array operations
```

### Quick Install - Full Multimodal Support
```bash
pip install PyPDF2 python-docx openpyxl beautifulsoup4 \
    Pillow lxml python-pptx
```

---

## Provider Requirements

### API Keys Required

| Provider | API Key Environment Variable | How to Get |
|----------|----------------------------|------------|
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| Anthropic | `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| Google | `GOOGLE_API_KEY` | https://makersuite.google.com/app/apikey |
| AWS Bedrock | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | AWS Console |
| Cohere | `COHERE_API_KEY` | https://cohere.ai/ |
| HuggingFace | `HUGGINGFACE_API_KEY` | https://huggingface.co/settings/tokens |
| Groq | `GROQ_API_KEY` | https://console.groq.com/ |
| Mistral | `MISTRAL_API_KEY` | https://console.mistral.ai/ |
| Together | `TOGETHER_API_KEY` | https://api.together.xyz/ |
| Replicate | `REPLICATE_API_TOKEN` | https://replicate.com/account |

### No API Key Required

- **Mock Provider** - Built-in, for testing
- **Ollama** - Local installation, no API key
- **Meta (Local)** - Direct model access, no API key

### Setting API Keys

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

**Windows:**
```cmd
set OPENAI_API_KEY=sk-...
set ANTHROPIC_API_KEY=sk-ant-...
set GOOGLE_API_KEY=...
```

**In Python:**
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'
```

**In Configuration:**
```python
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': 'sk-...',  # Direct in config
            'model': 'gpt-4'
        }
    }
}
```

---

## Installation Instructions

### Option 1: From Package (Recommended)

```bash
# 1. Extract package
tar -xzf abhikarta-llm-v3.1.6-FINAL.tar.gz
cd abhikarta-llm

# 2. Install in development mode
pip install -e .

# 3. Verify installation
python3 -c "import llm; print(f'Version: {llm.__version__}')"

# 4. Test with mock provider (no API key needed)
python3 examples/capabilities/01_basic_usage.py
```

### Option 2: With Virtual Environment

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 2. Extract and install
tar -xzf abhikarta-llm-v3.1.6-FINAL.tar.gz
cd abhikarta-llm
pip install -e .

# 3. Install optional dependencies
pip install PyPDF2 python-docx openpyxl beautifulsoup4 Pillow

# 4. Install provider SDKs (as needed)
pip install openai anthropic google-generativeai
```

### Option 3: Full Installation (All Features)

```bash
# Extract package
tar -xzf abhikarta-llm-v3.1.6-FINAL.tar.gz
cd abhikarta-llm

# Install package
pip install -e .

# Install all provider SDKs
pip install openai anthropic google-generativeai boto3 \
    cohere huggingface-hub groq mistralai together replicate

# Install all multimodal dependencies
pip install PyPDF2 python-docx openpyxl beautifulsoup4 \
    Pillow lxml python-pptx pdfplumber

# Verify
python3 -c "from llm.abstraction.facade import UnifiedLLMFacade; print('✅ Complete')"
```

### Option 4: Docker (Production)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy package
COPY abhikarta-llm/ /app/

# Install dependencies
RUN pip install -e . && \
    pip install openai anthropic google-generativeai && \
    pip install PyPDF2 python-docx openpyxl beautifulsoup4 Pillow

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run
CMD ["python3", "-m", "llm.abstraction"]
```

---

## Configuration Requirements

### Minimum Configuration

```python
# Works immediately with no API keys
config = {
    'providers': {
        'mock': {
            'enabled': True,
            'model': 'mock-model'
        }
    }
}
```

### Single Provider Configuration

```python
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': 'sk-...',  # or from env
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 2000
        }
    }
}
```

### Multi-Provider Configuration

```python
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'gpt-4'
        },
        'anthropic': {
            'enabled': True,
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'model': 'claude-3-opus-20240229'
        },
        'google': {
            'enabled': True,
            'api_key': os.getenv('GOOGLE_API_KEY'),
            'model': 'gemini-pro'
        }
    },
    'default_provider': 'openai',
    'timeout': 60,
    'retry_attempts': 3
}
```

---

## Platform Support

### Operating Systems

| OS | Status | Notes |
|----|--------|-------|
| **Linux** | ✅ Fully Supported | Ubuntu 20.04+, Debian, CentOS, RHEL |
| **macOS** | ✅ Fully Supported | macOS 10.15+ (Catalina or later) |
| **Windows** | ✅ Fully Supported | Windows 10/11, Windows Server 2019+ |
| **Docker** | ✅ Fully Supported | All platforms via Docker |
| **Cloud** | ✅ Fully Supported | AWS, GCP, Azure, Heroku |

### Architecture

| Architecture | Status | Notes |
|--------------|--------|-------|
| **x86_64 (AMD64)** | ✅ Fully Supported | Most common |
| **ARM64** | ✅ Supported | Apple Silicon (M1/M2), AWS Graviton |
| **ARM32** | ⚠️ Limited | Basic functionality only |

### Cloud Platforms

- ✅ **AWS** - Full support including Bedrock
- ✅ **Google Cloud** - Full support including Vertex AI
- ✅ **Azure** - Full support
- ✅ **Heroku** - Supported
- ✅ **DigitalOcean** - Supported
- ✅ **Railway** - Supported

---

## Security Requirements

### API Key Storage

**❌ DO NOT:**
- Hardcode API keys in source code
- Commit API keys to version control
- Share API keys in public repositories
- Store API keys in plaintext files

**✅ DO:**
- Use environment variables
- Use secrets management (AWS Secrets Manager, etc.)
- Use `.env` files (add to `.gitignore`)
- Rotate API keys regularly

### Example: Using .env File

```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

```python
# Load from .env
from dotenv import load_dotenv
import os

load_dotenv()

config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'gpt-4'
        }
    }
}
```

### Network Requirements

**Outbound Access Required:**
- OpenAI: `api.openai.com` (443)
- Anthropic: `api.anthropic.com` (443)
- Google: `generativelanguage.googleapis.com` (443)
- AWS: `bedrock.amazonaws.com` (443)
- Others: See provider documentation

**Firewall Rules:**
- Allow HTTPS (443) to provider endpoints
- Allow DNS resolution
- Optional: Set up proxy if needed

---

## Dependency Matrix

### By Feature

| Feature | Required Dependencies | Optional Dependencies |
|---------|----------------------|----------------------|
| **Basic Text LLM** | None | Provider SDK |
| **Streaming** | None | Provider SDK |
| **Chat** | None | Provider SDK |
| **Function Calling** | None | Provider SDK |
| **Vision (Images)** | None | Provider SDK, Pillow |
| **Audio Transcription** | None | Provider SDK |
| **PDF Parsing** | None | PyPDF2, pdfplumber |
| **DOCX Parsing** | None | python-docx |
| **Excel Parsing** | None | openpyxl |
| **HTML Parsing** | None | beautifulsoup4 |

### By Provider

| Provider | Required Packages | Optional Packages |
|----------|------------------|-------------------|
| Mock | None | None |
| OpenAI | openai | Pillow (for vision) |
| Anthropic | anthropic | Pillow (for vision) |
| Google | google-generativeai | None |
| AWS Bedrock | boto3, botocore | None |
| Cohere | cohere | None |
| HuggingFace | huggingface-hub | transformers |
| Groq | groq | None |
| Mistral | mistralai | None |
| Together | together | None |
| Ollama | None | None |
| Replicate | replicate | None |

---

## Troubleshooting

### Common Issues

**Issue: ImportError for provider SDK**
```bash
# Solution: Install provider SDK
pip install openai  # or anthropic, google-generativeai, etc.
```

**Issue: API key not found**
```bash
# Solution: Set environment variable
export OPENAI_API_KEY="sk-..."
```

**Issue: PDF parsing fails**
```bash
# Solution: Install PyPDF2
pip install PyPDF2
```

**Issue: Module not found**
```bash
# Solution: Install in editable mode
pip install -e .
```

**Issue: Permission denied (Linux/Mac)**
```bash
# Solution: Use virtual environment or --user flag
pip install --user -e .
```

### Verification Commands

```bash
# Check Python version
python3 --version

# Check if package installed
python3 -c "import llm; print(llm.__version__)"

# Check provider availability
python3 -c "from llm.abstraction.providers import PROVIDER_REGISTRY; print(len(PROVIDER_REGISTRY))"

# Check multimodal support
python3 -c "from llm.abstraction.multimodal import MultimodalHandler; print('✅')"

# Check document parser
python3 -c "from llm.abstraction.document_parser import DocumentParser; print('✅')"
```

---

## Summary of Requirements

### Minimum Requirements (Works Out of Box)
- Python 3.8+
- No external dependencies
- Works with mock provider

### Recommended Setup
- Python 3.10+
- Virtual environment
- At least one provider SDK (openai, anthropic, etc.)
- Multimodal dependencies (PyPDF2, python-docx, etc.)

### Full Production Setup
- Python 3.11+
- Virtual environment or Docker
- All provider SDKs
- All multimodal dependencies
- Secrets management
- Monitoring and logging

---

## Support & Contact

For questions about requirements or installation:

**Email:** ajsinha@gmail.com  
**Documentation:** See `/docs` directory  
**Examples:** See `/examples` directory

---

**Version:** 3.1.6  
**Date:** November 4, 2025  
**Status:** ✅ Production Ready

---

<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6
-->
