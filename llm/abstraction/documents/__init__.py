"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4

Document Processing Module - Transparent file handling
"""

from .processor import DocumentProcessor
from .loaders import (
    load_pdf,
    load_docx,
    load_csv,
    load_txt,
    load_json,
    auto_load
)

__all__ = [
    'DocumentProcessor',
    'load_pdf',
    'load_docx',
    'load_csv',
    'load_txt',
    'load_json',
    'auto_load',
]

"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.4
"""
