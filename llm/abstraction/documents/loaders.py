"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4

Document Loaders - Load various file formats
"""

import os
import json
from typing import Union, Dict, List, Any
from pathlib import Path


def load_txt(filepath: str) -> str:
    """
    Load text file.
    
    Args:
        filepath: Path to .txt file
    
    Returns:
        Text content
    
    Example:
        text = load_txt("document.txt")
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def load_json(filepath: str) -> Union[Dict, List]:
    """
    Load JSON file.
    
    Args:
        filepath: Path to .json file
    
    Returns:
        Parsed JSON data
    
    Example:
        data = load_json("data.json")
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_csv(filepath: str, as_dict: bool = True) -> Union[List[Dict], List[List]]:
    """
    Load CSV file.
    
    Args:
        filepath: Path to .csv file
        as_dict: If True, return list of dicts. If False, return list of lists.
    
    Returns:
        CSV data
    
    Example:
        data = load_csv("data.csv")
        for row in data:
            print(row['column_name'])
    """
    import csv
    
    with open(filepath, 'r', encoding='utf-8') as f:
        if as_dict:
            reader = csv.DictReader(f)
            return list(reader)
        else:
            reader = csv.reader(f)
            return list(reader)


def load_pdf(filepath: str, page_numbers: List[int] = None) -> str:
    """
    Load PDF file and extract text.
    
    Args:
        filepath: Path to .pdf file
        page_numbers: Optional list of page numbers to extract (0-indexed)
    
    Returns:
        Extracted text
    
    Example:
        text = load_pdf("document.pdf")
        # Or specific pages
        text = load_pdf("document.pdf", page_numbers=[0, 1, 2])
    """
    try:
        import PyPDF2
        
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            if page_numbers:
                pages = [reader.pages[i] for i in page_numbers if i < len(reader.pages)]
            else:
                pages = reader.pages
            
            text = []
            for page in pages:
                text.append(page.extract_text())
            
            return '\n\n'.join(text)
    
    except ImportError:
        # Fallback: try pdfplumber
        try:
            import pdfplumber
            
            with pdfplumber.open(filepath) as pdf:
                if page_numbers:
                    pages = [pdf.pages[i] for i in page_numbers if i < len(pdf.pages)]
                else:
                    pages = pdf.pages
                
                text = []
                for page in pages:
                    text.append(page.extract_text())
                
                return '\n\n'.join(text)
        
        except ImportError:
            raise ImportError(
                "PDF support requires PyPDF2 or pdfplumber. "
                "Install with: pip install PyPDF2 or pip install pdfplumber"
            )


def load_docx(filepath: str) -> str:
    """
    Load DOCX file and extract text.
    
    Args:
        filepath: Path to .docx file
    
    Returns:
        Extracted text
    
    Example:
        text = load_docx("document.docx")
    """
    try:
        from docx import Document
        
        doc = Document(filepath)
        paragraphs = [para.text for para in doc.paragraphs]
        return '\n\n'.join(paragraphs)
    
    except ImportError:
        raise ImportError(
            "DOCX support requires python-docx. "
            "Install with: pip install python-docx"
        )


def auto_load(filepath: str, **kwargs) -> Any:
    """
    Automatically detect file type and load appropriately.
    
    Args:
        filepath: Path to file
        **kwargs: Additional arguments passed to specific loader
    
    Returns:
        File content in appropriate format
    
    Example:
        content = auto_load("document.pdf")
        content = auto_load("data.json")
        content = auto_load("file.txt")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    extension = filepath.suffix.lower()
    
    loaders = {
        '.txt': load_txt,
        '.json': load_json,
        '.csv': load_csv,
        '.pdf': load_pdf,
        '.docx': load_docx,
        '.doc': load_docx,
    }
    
    if extension in loaders:
        return loaders[extension](str(filepath), **kwargs)
    else:
        # Try to read as text
        try:
            return load_txt(str(filepath))
        except Exception as e:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join(loaders.keys())}"
            )


def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Args:
        filepath: Path to file
    
    Returns:
        Dictionary with file information
    
    Example:
        info = get_file_info("document.pdf")
        print(f"Size: {info['size_mb']:.2f} MB")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    stat = filepath.stat()
    
    return {
        'name': filepath.name,
        'extension': filepath.suffix,
        'size_bytes': stat.st_size,
        'size_kb': stat.st_size / 1024,
        'size_mb': stat.st_size / (1024 * 1024),
        'modified': stat.st_mtime,
        'is_file': filepath.is_file(),
        'is_dir': filepath.is_dir(),
    }


__all__ = [
    'load_txt',
    'load_json',
    'load_csv',
    'load_pdf',
    'load_docx',
    'auto_load',
    'get_file_info',
]


"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.4
"""
