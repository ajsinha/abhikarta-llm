<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.6
-->

# Abhikarta LLM v3.1.6

**Universal LLM Abstraction Framework with Multimodal Support**

A production-ready Python framework for working with 13 LLM providers through a single, unified API. Now with comprehensive multimodal support for images, audio, video, and document parsing.

## ✨ Key Features

- **13 LLM Providers** - OpenAI, Anthropic, Google, AWS Bedrock, Cohere, HuggingFace, Meta, Groq, Mistral, Together, Ollama, Replicate, Mock
- **Multimodal Support** ✨ - Images, audio, video processing
- **Document Parsing** ✨ - PDF, DOCX, Excel, HTML, and more
- **Unified API** - Write once, use with any provider
- **Production Ready** - Comprehensive error handling, type safety
- **Full Featured** - Streaming, chat, function calling, embeddings

## 🎨 NEW in v3.1.6: Multimodal & Document Support

### Multimodal Processing
```python
from llm.abstraction.multimodal import MultimodalHandler

handler = MultimodalHandler()

# Load and process images
image = handler.load_image('photo.jpg')
response = facade.complete("Describe this image", media=[image])

# Load and transcribe audio
audio = handler.load_audio('meeting.mp3')
transcript = facade.transcribe(audio)

# Load and analyze video
video = handler.load_video('presentation.mp4')
response = facade.complete("Summarize video", media=[video])
```

### Document Parsing
```python
from llm.abstraction.document_parser import DocumentParser

parser = DocumentParser()

# Parse various formats
pdf_doc = parser.parse('report.pdf')
docx_doc = parser.parse('document.docx')
excel_doc = parser.parse('data.xlsx')

# Use with LLM
response = facade.complete(f"Summarize: {pdf_doc.text}")
```

## 🚀 Quick Start

```python
from llm.abstraction.facade import UnifiedLLMFacade

# Configure provider (no API key needed for mock)
config = {
    'providers': {
        'mock': {
            'enabled': True,
            'model': 'mock-model'
        }
    }
}

# Create facade and use it
facade = UnifiedLLMFacade(config)
response = facade.complete("What is Python?")
print(response.text)
```

## 📦 Installation

```bash
# Extract package
tar -xzf abhikarta-llm-v3.1.6-FINAL.tar.gz
cd abhikarta-llm

# Install (optional)
pip install -e .

# For multimodal support (optional)
pip install PyPDF2 python-docx openpyxl beautifulsoup4 Pillow
```

## 📖 Examples

20+ complete examples in `examples/capabilities/`:

```bash
# Basic examples
python examples/capabilities/01_basic_usage.py
python examples/capabilities/02_multiple_providers.py

# Multimodal examples (NEW)
python examples/capabilities/16_multimodal_images.py
python examples/capabilities/18_document_parsing.py
python examples/capabilities/20_document_qa.py
```

## 🎯 Supported Providers - Complete List

### Cloud Providers (8)

| Provider | Models | Multimodal | Speed | Cost |
|----------|--------|------------|-------|------|
| **OpenAI** | GPT-3.5, GPT-4, GPT-4V | ✅ Vision | Fast | $$$ |
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) | ✅ Vision | Fast | $$$ |
| **Google** | Gemini Pro, Gemini Vision | ✅ Vision | Fast | $$ |
| **AWS Bedrock** | Claude, Llama, Titan, etc. | ✅ Various | Fast | $$$ |
| **Cohere** | Command, Command-R | ❌ | Fast | $$ |
| **Groq** | Mixtral, Llama 2/3 | ❌ | Ultra-fast | $ |
| **Mistral** | Mistral 7B, Mixtral 8x7B | ❌ | Fast | $$ |
| **Together** | 50+ open source models | ❌ | Fast | $ |

### Self-Hosted / Community (4)

| Provider | Models | Multimodal | Speed | Cost |
|----------|--------|------------|-------|------|
| **Ollama** | Llama, LLaVA, Mistral | ✅ LLaVA | Medium | FREE |
| **HuggingFace** | 100,000+ community models | ✅ Various | Varies | FREE/$ |
| **Replicate** | Stable Diffusion, Llama, etc. | ✅ Various | Medium | $ |
| **Meta** | Llama 2, Llama 3 | ❌ | Medium | FREE |

### Testing (1)

| Provider | Models | Multimodal | Speed | Cost |
|----------|--------|------------|-------|------|
| **Mock** | Testing only | ✅ Mock | Instant | FREE |

## 🎨 Multimodal Capabilities

### Supported Formats

**Images:**
- ✅ JPG, JPEG, PNG, GIF, BMP, WebP, SVG
- Use cases: Image description, OCR, chart analysis, visual Q&A

**Audio:**
- ✅ MP3, WAV, M4A, FLAC, AAC, OGG
- Use cases: Transcription, meeting summaries, audio analysis

**Video:**
- ✅ MP4, AVI, MOV, MKV, WebM, FLV
- Use cases: Video description, content analysis, frame extraction

**Documents:**
- ✅ PDF, DOC, DOCX, PPTX, TXT, MD, HTML
- ✅ CSV, XLSX, JSON, XML
- Use cases: Document Q&A, text extraction, data parsing

### Vision-Capable Models

| Provider | Model | Features |
|----------|-------|----------|
| OpenAI | GPT-4 Vision | Best quality, detailed descriptions |
| Anthropic | Claude 3 Opus/Sonnet | Long context, document analysis |
| Google | Gemini Pro Vision | Fast, multimodal reasoning |
| Ollama | LLaVA, BakLLaVA | Local, FREE, privacy |

## 🔧 Configuration Examples

### Vision Model Configuration

**OpenAI GPT-4 Vision:**
```python
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': 'sk-...',
            'model': 'gpt-4-vision-preview'
        }
    }
}

# Use with image
from llm.abstraction.multimodal import MultimodalHandler
handler = MultimodalHandler()
image = handler.load_image('chart.png')

facade = UnifiedLLMFacade(config)
response = facade.complete("Analyze this chart", media=[image])
```

**Anthropic Claude 3:**
```python
config = {
    'providers': {
        'anthropic': {
            'enabled': True,
            'api_key': 'sk-ant-...',
            'model': 'claude-3-opus-20240229'
        }
    }
}

# Claude 3 supports images natively
response = facade.complete("Describe image", media=[image])
```

**Google Gemini Vision:**
```python
config = {
    'providers': {
        'google': {
            'enabled': True,
            'api_key': '...',
            'model': 'gemini-pro-vision'
        }
    }
}
```

### Document Processing

```python
from llm.abstraction.document_parser import DocumentParser

parser = DocumentParser()

# Parse different formats
pdf = parser.parse('report.pdf')
print(f"Pages: {pdf.page_count}")
print(f"Text: {pdf.text}")

docx = parser.parse('document.docx')
excel = parser.parse('data.xlsx')
html = parser.parse('page.html')

# Use with LLM for Q&A
response = facade.complete(f"""
Document: {pdf.text}

Question: What are the key findings?
""")
```

## 📚 Complete Feature List

### Core Features
- ✅ 13 LLM providers
- ✅ Unified API
- ✅ Streaming support
- ✅ Chat and completion modes
- ✅ Parameter control
- ✅ Error handling

### Multimodal Features (NEW v3.1.6)
- ✅ Image processing (JPG, PNG, etc.)
- ✅ Audio transcription (MP3, WAV, etc.)
- ✅ Video analysis (MP4, AVI, etc.)
- ✅ Document parsing (PDF, DOCX, etc.)
- ✅ Base64 encoding
- ✅ MIME type detection

### Document Formats (NEW v3.1.6)
- ✅ PDF - PyPDF2
- ✅ DOCX - python-docx
- ✅ Excel - openpyxl
- ✅ HTML - BeautifulSoup4
- ✅ CSV, JSON, XML - built-in
- ✅ TXT, MD - built-in

### Advanced Features
- ✅ Function calling / Tools
- ✅ Streaming utilities (10 functions)
- ✅ Provider registry
- ✅ Metadata tracking

## 🎯 Use Cases

### Document Analysis
```python
# Extract and analyze document
doc = parser.parse('contract.pdf')
response = facade.complete(f"Summarize key terms: {doc.text}")
```

### Image Analysis
```python
# Describe image
image = handler.load_image('product.jpg')
response = facade.complete("Describe this product", media=[image])
```

### Audio Transcription
```python
# Transcribe meeting
audio = handler.load_audio('meeting.mp3')
transcript = facade.transcribe(audio)
```

### Multi-Format Processing
```python
# Combine document and image
doc = parser.parse('report.pdf')
chart = handler.load_image('chart.png')

response = facade.complete(f"""
Report: {doc.text[:1000]}

Analyze the chart and relate to the report.
""", media=[chart])
```

## ✅ What's New in v3.1.6

- ✅ **Multimodal support** - Images, audio, video
- ✅ **Document parsing** - 11 formats supported
- ✅ **Vision models** - GPT-4V, Claude 3, Gemini
- ✅ **Audio transcription** - Whisper, Speech-to-Text
- ✅ **5 new examples** - Multimodal demos
- ✅ **Enhanced documentation** - Complete guides

## 🧪 Testing

```bash
# Test imports
python3 -c "from llm.abstraction.facade import UnifiedLLMFacade; print('✅')"

# Test multimodal
python3 -c "from llm.abstraction.multimodal import MultimodalHandler; print('✅')"

# Test document parser
python3 -c "from llm.abstraction.document_parser import DocumentParser; print('✅')"

# Run examples
python examples/capabilities/01_basic_usage.py
python examples/capabilities/16_multimodal_images.py
```

## 📊 Feature Comparison

| Feature | v3.1.3 | v3.1.6 |
|---------|--------|--------|
| LLM Providers | 13 | 13 |
| Text completion | ✅ | ✅ |
| Streaming | ✅ | ✅ |
| **Image support** | ❌ | ✅ |
| **Audio support** | ❌ | ✅ |
| **Video support** | ❌ | ✅ |
| **Document parsing** | ❌ | ✅ |
| Examples | 15 | 20 |

## 📄 License

Copyright 2025-2030 all rights reserved  
Ashutosh Sinha  
Email: ajsinha@gmail.com

## 🤝 Support

For questions or issues, contact: ajsinha@gmail.com

---

**Version:** 3.1.6  
**Providers:** 13 (8 cloud, 4 self-hosted, 1 mock)  
**Multimodal:** ✅ Images, Audio, Video  
**Documents:** ✅ 11 formats supported  
**Examples:** 20 (15 core + 5 multimodal)  
**Status:** ✅ Production Ready  
**Quality:** ⭐⭐⭐⭐⭐ (5/5)

---

<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6
-->
