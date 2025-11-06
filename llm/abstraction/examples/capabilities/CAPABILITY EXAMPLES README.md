<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4
-->

# Abhikarta LLM - Capability Examples

This directory contains 20 complete examples demonstrating core capabilities of Abhikarta LLM.

## Quick Start

```bash
# Run any example
python 01_basic_usage.py
python 16_multimodal_images.py
python 18_document_parsing.py
```

## Examples Overview

### Core Features (1-10)

| Example | File | Description |
|---------|------|-------------|
| 01 | `01_basic_usage.py` | Basic text completion |
| 02 | `02_multiple_providers.py` | Configure multiple providers |
| 03 | `03_streaming.py` | Streaming responses |
| 04 | `04_chat_messages.py` | Chat with message history |
| 05 | `05_parameters.py` | Temperature & parameters |
| 06 | `06_provider_switching.py` | Switch between providers |
| 07 | `07_error_handling.py` | Error handling patterns |
| 08 | `08_metadata_usage.py` | Access metadata & usage stats |
| 09 | `09_batch_requests.py` | Batch processing |
| 10 | `10_provider_info.py` | Provider information |

### Provider-Specific Examples (11-15)

| Example | File | Provider | Description |
|---------|------|----------|-------------|
| 11 | `11_awsbedrock_example.py` | AWS Bedrock | Enterprise AWS integration |
| 12 | `12_cohere_example.py` | Cohere | Command models |
| 13 | `13_huggingface_example.py` | HuggingFace | 100,000+ models |
| 14 | `14_meta_llama_example.py` | Meta | Direct Llama access |
| 15 | `15_replicate_example.py` | Replicate | Pay-per-use models |

### Multimodal & Document Processing (16-20) - NEW ✨

| Example | File | Feature | Description |
|---------|------|---------|-------------|
| 16 | `16_multimodal_images.py` | Images | Image processing & vision |
| 17 | `17_multimodal_audio.py` | Audio | Audio transcription |
| 18 | `18_document_parsing.py` | Documents | PDF, DOCX, Excel parsing |
| 19 | `19_multimodal_complete.py` | Complete | Full multimodal workflow |
| 20 | `20_document_qa.py` | Q&A | Document question answering |

## New Features in v3.1.4 ✨

### Multimodal Support
- **Images**: JPG, PNG, GIF, BMP, WebP, SVG
- **Audio**: MP3, WAV, M4A, FLAC, AAC, OGG
- **Video**: MP4, AVI, MOV, MKV, WebM, FLV

### Document Formats
- **Office**: PDF, DOC, DOCX, PPTX
- **Data**: CSV, XLSX, JSON, XML
- **Web**: HTML, MD, TXT

## Requirements

- **No API keys required** - Examples 01-10 work with the mock provider
- To use real providers (examples 11-15), add API keys to config
- Multimodal examples (16-20) require vision-capable models

## Multimodal Dependencies (Optional)

```bash
# For full multimodal support
pip install PyPDF2           # PDF parsing
pip install python-docx      # DOCX parsing
pip install openpyxl         # Excel parsing
pip install beautifulsoup4   # HTML parsing
pip install Pillow           # Image processing
```

## Usage Patterns

### Basic Usage
```python
from llm.abstraction.facade import UnifiedLLMFacade

config = {'providers': {'mock': {'enabled': True}}}
facade = UnifiedLLMFacade(config)
response = facade.complete("Hello!")
print(response.text)
```

### Multimodal Usage
```python
from llm.abstraction.multimodal import MultimodalHandler

handler = MultimodalHandler()

# Load image
image = handler.load_image('photo.jpg')

# Use with vision model
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'model': 'gpt-4-vision-preview',
            'api_key': 'your-key'
        }
    }
}
facade = UnifiedLLMFacade(config)
response = facade.complete("Describe this image", media=[image])
```

### Document Parsing
```python
from llm.abstraction.document_parser import DocumentParser

parser = DocumentParser()

# Parse PDF
doc = parser.parse('report.pdf')
print(f"Text: {doc.text}")
print(f"Pages: {doc.page_count}")

# Use with LLM
response = facade.complete(f"Summarize: {doc.text}")
```

## Supported Media Types

### Images (Vision Models)
| Provider | Support | Models |
|----------|---------|--------|
| OpenAI | ✅ | GPT-4 Vision |
| Anthropic | ✅ | Claude 3 Opus/Sonnet |
| Google | ✅ | Gemini Pro Vision |
| Ollama | ✅ | LLaVA, BakLLaVA |

### Audio (Transcription)
| Provider | Support | Models |
|----------|---------|--------|
| OpenAI | ✅ | Whisper |
| Google | ✅ | Speech-to-Text |
| AWS | ✅ | Transcribe |

### Documents (All Providers)
All text-based LLM providers can process extracted document text.

## Provider Setup Instructions

### Vision-Capable Providers

**OpenAI GPT-4 Vision:**
```python
config = {
    'providers': {
        'openai': {
            'enabled': True,
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'gpt-4-vision-preview'
        }
    }
}
```

**Anthropic Claude 3:**
```python
config = {
    'providers': {
        'anthropic': {
            'enabled': True,
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'model': 'claude-3-opus-20240229'
        }
    }
}
```

**Google Gemini Vision:**
```python
config = {
    'providers': {
        'google': {
            'enabled': True,
            'api_key': os.getenv('GOOGLE_API_KEY'),
            'model': 'gemini-pro-vision'
        }
    }
}
```

## Use Cases

### Document Analysis
- Extract text from PDFs, DOCX, Excel
- Answer questions about documents
- Summarize long documents
- Compare multiple documents

### Image Analysis
- Describe images
- Extract text from images (OCR)
- Analyze charts and graphs
- Visual question answering

### Audio Processing
- Transcribe meetings
- Convert speech to text
- Analyze audio content
- Create summaries from recordings

### Combined Workflows
- Document + image analysis
- Multi-format data extraction
- Comprehensive content analysis

## Next Steps

1. Run the examples (start with 01-10)
2. Try multimodal examples (16-20)
3. Install optional dependencies as needed
4. Build your own multimodal application!

---

<!--
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.4
-->
