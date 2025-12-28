"""
Pre-built Tools Library - General Purpose Tools

This module provides commonly used general-purpose tools including:
- Web/Internet search
- Document handling
- File operations
- System utilities
- Network operations

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import logging
import json
import os
import re
import mimetypes
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode, urlparse, parse_qs

from ..base_tool import (
    BaseTool, ToolMetadata, ToolSchema, ToolParameter,
    ToolResult, ToolType, ToolCategory
)
from ..function_tool import FunctionTool

logger = logging.getLogger(__name__)


# =============================================================================
# WEB/INTERNET SEARCH TOOLS
# =============================================================================

def web_search(query: str, num_results: int = 10, search_type: str = "general") -> Dict[str, Any]:
    """
    Search the web for information.
    
    Args:
        query: Search query string
        num_results: Number of results to return (1-50)
        search_type: Type of search - 'general', 'news', 'images', 'scholarly'
        
    Returns:
        Search results with titles, URLs, and snippets
    """
    # This is a simulation - in production, integrate with actual search API
    # like Google Custom Search, Bing Search, DuckDuckGo, or SerpAPI
    
    num_results = min(max(1, num_results), 50)
    
    return {
        "query": query,
        "search_type": search_type,
        "num_results": num_results,
        "results": [
            {
                "position": i + 1,
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a sample search result snippet for query: {query}",
                "source": "example.com"
            }
            for i in range(num_results)
        ],
        "note": "Connect to a real search API (Google, Bing, SerpAPI) for actual results"
    }


def web_fetch(url: str, include_html: bool = False, timeout: int = 30) -> Dict[str, Any]:
    """
    Fetch content from a web URL.
    
    Args:
        url: URL to fetch
        include_html: Whether to include raw HTML in response
        timeout: Request timeout in seconds
        
    Returns:
        Fetched content with metadata
    """
    import requests
    from urllib.parse import urlparse
    
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {"success": False, "error": "Invalid URL format"}
        
        headers = {
            "User-Agent": "Abhikarta-LLM/1.2.2 (Web Fetch Tool)"
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        
        content_type = response.headers.get('Content-Type', '')
        
        result = {
            "success": True,
            "url": url,
            "status_code": response.status_code,
            "content_type": content_type,
            "content_length": len(response.content),
            "headers": dict(response.headers)
        }
        
        if 'text' in content_type or 'json' in content_type:
            result["text_content"] = response.text[:10000]  # Limit to 10KB
            if include_html:
                result["html"] = response.text
        
        return result
        
    except requests.Timeout:
        return {"success": False, "error": f"Request timed out after {timeout}s"}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def intranet_search(query: str, sites: List[str] = None, 
                    file_types: List[str] = None) -> Dict[str, Any]:
    """
    Search internal/intranet resources.
    
    Args:
        query: Search query string
        sites: List of intranet site URLs to search
        file_types: Filter by file types (pdf, docx, xlsx, etc.)
        
    Returns:
        Search results from internal resources
    """
    # This is a placeholder - integrate with actual enterprise search
    # like Elasticsearch, SharePoint Search, or custom intranet indexer
    
    return {
        "query": query,
        "sites": sites or ["intranet.company.com"],
        "file_types": file_types or ["all"],
        "results": [],
        "total_results": 0,
        "note": "Configure enterprise search integration (Elasticsearch, SharePoint) for actual results"
    }


def news_search(query: str, days_back: int = 7, 
                sources: List[str] = None) -> Dict[str, Any]:
    """
    Search news articles.
    
    Args:
        query: News search query
        days_back: How many days back to search
        sources: Specific news sources to search
        
    Returns:
        News articles matching the query
    """
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return {
        "query": query,
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        },
        "sources": sources or ["all"],
        "articles": [],
        "note": "Connect to a news API (NewsAPI, GDELT, Google News) for actual results"
    }


# =============================================================================
# DOCUMENT HANDLING TOOLS
# =============================================================================

def read_document(file_path: str, extract_text: bool = True) -> Dict[str, Any]:
    """
    Read and extract content from documents.
    
    Args:
        file_path: Path to the document file
        extract_text: Whether to extract text content
        
    Returns:
        Document content and metadata
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}
    
    file_ext = os.path.splitext(file_path)[1].lower()
    file_size = os.path.getsize(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    
    result = {
        "success": True,
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "extension": file_ext,
        "size_bytes": file_size,
        "mime_type": mime_type
    }
    
    if extract_text:
        try:
            if file_ext in ['.txt', '.md', '.json', '.csv', '.xml', '.html']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    result["text_content"] = f.read()[:50000]  # Limit to 50KB
            elif file_ext == '.pdf':
                result["text_content"] = "[PDF extraction requires PyPDF2 or pdfplumber]"
            elif file_ext in ['.docx', '.doc']:
                result["text_content"] = "[Word extraction requires python-docx]"
            elif file_ext in ['.xlsx', '.xls']:
                result["text_content"] = "[Excel extraction requires openpyxl or xlrd]"
            else:
                result["text_content"] = "[Binary file - text extraction not supported]"
        except Exception as e:
            result["text_content"] = f"[Error extracting text: {e}]"
    
    return result


def write_document(file_path: str, content: str, 
                   append: bool = False, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    Write content to a document file.
    
    Args:
        file_path: Path to write the file
        content: Content to write
        append: Whether to append to existing file
        encoding: File encoding
        
    Returns:
        Write operation result
    """
    try:
        # Create directory if needed
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        return {
            "success": True,
            "file_path": file_path,
            "bytes_written": len(content.encode(encoding)),
            "mode": "append" if append else "write"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def convert_document(input_path: str, output_format: str, 
                     output_path: str = None) -> Dict[str, Any]:
    """
    Convert document between formats.
    
    Args:
        input_path: Path to input document
        output_format: Target format (pdf, docx, txt, html, md)
        output_path: Optional output path
        
    Returns:
        Conversion result with output file path
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": f"Input file not found: {input_path}"}
    
    input_ext = os.path.splitext(input_path)[1].lower()
    
    if not output_path:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.{output_format}"
    
    # Simple text-based conversions
    text_formats = ['.txt', '.md', '.json', '.csv', '.xml', '.html']
    
    if input_ext in text_formats and output_format in ['txt', 'md']:
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "output_format": output_format
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {
        "success": False,
        "error": f"Conversion from {input_ext} to {output_format} requires additional libraries",
        "note": "Install pandoc, pypandoc, or specific format libraries for full conversion support"
    }


def extract_document_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from a document.
    
    Args:
        file_path: Path to the document
        
    Returns:
        Document metadata (author, creation date, etc.)
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}
    
    stat = os.stat(file_path)
    
    return {
        "success": True,
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "size_bytes": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
        "note": "Full metadata extraction (author, title) requires format-specific libraries"
    }


# =============================================================================
# FILE OPERATIONS TOOLS
# =============================================================================

def list_files(directory: str, pattern: str = "*", 
               recursive: bool = False, max_depth: int = 3) -> Dict[str, Any]:
    """
    List files in a directory.
    
    Args:
        directory: Directory path to list
        pattern: Glob pattern to filter files
        recursive: Whether to search recursively
        max_depth: Maximum recursion depth
        
    Returns:
        List of files matching the pattern
    """
    import fnmatch
    
    if not os.path.exists(directory):
        return {"success": False, "error": f"Directory not found: {directory}"}
    
    if not os.path.isdir(directory):
        return {"success": False, "error": f"Not a directory: {directory}"}
    
    files = []
    
    def scan_dir(path, depth):
        if depth > max_depth:
            return
        try:
            for entry in os.scandir(path):
                if entry.is_file() and fnmatch.fnmatch(entry.name, pattern):
                    files.append({
                        "name": entry.name,
                        "path": entry.path,
                        "size": entry.stat().st_size,
                        "modified": datetime.fromtimestamp(entry.stat().st_mtime).isoformat()
                    })
                elif recursive and entry.is_dir() and not entry.name.startswith('.'):
                    scan_dir(entry.path, depth + 1)
        except PermissionError:
            pass
    
    scan_dir(directory, 0)
    
    return {
        "success": True,
        "directory": directory,
        "pattern": pattern,
        "recursive": recursive,
        "files": files[:1000],  # Limit to 1000 files
        "total_count": len(files)
    }


def copy_file(source: str, destination: str, 
              overwrite: bool = False) -> Dict[str, Any]:
    """
    Copy a file to a new location.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite existing file
        
    Returns:
        Copy operation result
    """
    import shutil
    
    if not os.path.exists(source):
        return {"success": False, "error": f"Source file not found: {source}"}
    
    if os.path.exists(destination) and not overwrite:
        return {"success": False, "error": f"Destination exists and overwrite=False: {destination}"}
    
    try:
        # Create destination directory if needed
        dest_dir = os.path.dirname(destination)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)
        
        shutil.copy2(source, destination)
        
        return {
            "success": True,
            "source": source,
            "destination": destination,
            "bytes_copied": os.path.getsize(destination)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_file(source: str, destination: str, 
              overwrite: bool = False) -> Dict[str, Any]:
    """
    Move a file to a new location.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite existing file
        
    Returns:
        Move operation result
    """
    import shutil
    
    if not os.path.exists(source):
        return {"success": False, "error": f"Source file not found: {source}"}
    
    if os.path.exists(destination) and not overwrite:
        return {"success": False, "error": f"Destination exists and overwrite=False: {destination}"}
    
    try:
        dest_dir = os.path.dirname(destination)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)
        
        shutil.move(source, destination)
        
        return {
            "success": True,
            "source": source,
            "destination": destination
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_file(file_path: str, confirm: bool = True) -> Dict[str, Any]:
    """
    Delete a file.
    
    Args:
        file_path: Path to file to delete
        confirm: Require confirmation flag
        
    Returns:
        Delete operation result
    """
    if not confirm:
        return {"success": False, "error": "Delete requires confirm=True"}
    
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}
    
    try:
        os.remove(file_path)
        return {"success": True, "deleted": file_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# SYSTEM UTILITIES
# =============================================================================

def get_system_info() -> Dict[str, Any]:
    """
    Get system information.
    
    Returns:
        System information including OS, memory, disk usage
    """
    import platform
    
    info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node()
    }
    
    # Try to get memory info
    try:
        import psutil
        mem = psutil.virtual_memory()
        info["memory"] = {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "percent_used": mem.percent
        }
        
        disk = psutil.disk_usage('/')
        info["disk"] = {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": disk.percent
        }
    except ImportError:
        info["memory"] = "psutil not installed"
        info["disk"] = "psutil not installed"
    
    return info


def execute_shell_command(command: str, timeout: int = 60, 
                          shell: bool = True) -> Dict[str, Any]:
    """
    Execute a shell command safely.
    
    Args:
        command: Command to execute
        timeout: Command timeout in seconds
        shell: Whether to use shell execution
        
    Returns:
        Command output and return code
    """
    import subprocess
    
    # Security: Block dangerous commands
    dangerous_patterns = [
        'rm -rf /', 'mkfs', 'dd if=', ':(){ :', 'fork bomb',
        'chmod -R 777 /', 'chown -R', 'sudo rm', 'shutdown',
        'reboot', 'poweroff', 'init 0', 'init 6'
    ]
    
    for pattern in dangerous_patterns:
        if pattern.lower() in command.lower():
            return {
                "success": False,
                "error": f"Blocked: Potentially dangerous command pattern detected"
            }
    
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout[:10000],  # Limit output
            "stderr": result.stderr[:5000]
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_environment_variable(name: str, default: str = None) -> Dict[str, Any]:
    """
    Get an environment variable value.
    
    Args:
        name: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value
    """
    value = os.environ.get(name, default)
    return {
        "name": name,
        "value": value,
        "exists": name in os.environ
    }


def set_environment_variable(name: str, value: str) -> Dict[str, Any]:
    """
    Set an environment variable (for current process).
    
    Args:
        name: Environment variable name
        value: Value to set
        
    Returns:
        Operation result
    """
    try:
        os.environ[name] = value
        return {"success": True, "name": name, "value": value}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# NETWORK TOOLS
# =============================================================================

def check_url_status(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check the status of a URL.
    
    Args:
        url: URL to check
        timeout: Request timeout
        
    Returns:
        URL status and response time
    """
    import requests
    import time
    
    try:
        start = time.time()
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        elapsed = (time.time() - start) * 1000
        
        return {
            "success": True,
            "url": url,
            "status_code": response.status_code,
            "response_time_ms": round(elapsed, 2),
            "final_url": response.url,
            "redirected": response.url != url
        }
    except requests.RequestException as e:
        return {"success": False, "url": url, "error": str(e)}


def ping_host(host: str, count: int = 4) -> Dict[str, Any]:
    """
    Ping a host to check connectivity.
    
    Args:
        host: Hostname or IP to ping
        count: Number of ping packets
        
    Returns:
        Ping results
    """
    import subprocess
    import platform
    
    # Platform-specific ping command
    if platform.system().lower() == 'windows':
        cmd = ['ping', '-n', str(count), host]
    else:
        cmd = ['ping', '-c', str(count), host]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return {
            "success": result.returncode == 0,
            "host": host,
            "output": result.stdout,
            "reachable": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "host": host, "error": "Ping timed out"}
    except Exception as e:
        return {"success": False, "host": host, "error": str(e)}


def dns_lookup(hostname: str, record_type: str = "A") -> Dict[str, Any]:
    """
    Perform DNS lookup.
    
    Args:
        hostname: Hostname to lookup
        record_type: DNS record type (A, AAAA, MX, CNAME, TXT, NS)
        
    Returns:
        DNS lookup results
    """
    import socket
    
    try:
        if record_type.upper() == "A":
            ips = socket.gethostbyname_ex(hostname)
            return {
                "success": True,
                "hostname": hostname,
                "record_type": "A",
                "canonical_name": ips[0],
                "aliases": ips[1],
                "addresses": ips[2]
            }
        else:
            # For other record types, try socket.getaddrinfo
            results = socket.getaddrinfo(hostname, None)
            addresses = list(set(r[4][0] for r in results))
            return {
                "success": True,
                "hostname": hostname,
                "addresses": addresses
            }
    except socket.gaierror as e:
        return {"success": False, "hostname": hostname, "error": str(e)}


def parse_url(url: str) -> Dict[str, Any]:
    """
    Parse a URL into its components.
    
    Args:
        url: URL to parse
        
    Returns:
        Parsed URL components
    """
    from urllib.parse import urlparse, parse_qs
    
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        return {
            "success": True,
            "original_url": url,
            "scheme": parsed.scheme,
            "netloc": parsed.netloc,
            "hostname": parsed.hostname,
            "port": parsed.port,
            "path": parsed.path,
            "query": parsed.query,
            "query_params": query_params,
            "fragment": parsed.fragment,
            "username": parsed.username,
            "password": "***" if parsed.password else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# ENCODING/DECODING TOOLS
# =============================================================================

def url_encode(text: str) -> str:
    """URL encode a string."""
    from urllib.parse import quote
    return quote(text)


def url_decode(text: str) -> str:
    """URL decode a string."""
    from urllib.parse import unquote
    return unquote(text)


def html_encode(text: str) -> str:
    """HTML encode special characters."""
    import html
    return html.escape(text)


def html_decode(text: str) -> str:
    """HTML decode special characters."""
    import html
    return html.unescape(text)


# =============================================================================
# TOOL REGISTRATION
# =============================================================================

def get_general_tools() -> List[FunctionTool]:
    """Get all general-purpose tools."""
    tools = []
    
    # Web/Search tools
    tools.append(FunctionTool.from_function(
        web_search,
        name="web_search",
        description="Search the web for information. Returns search results with titles, URLs, and snippets.",
        category=ToolCategory.SEARCH
    ))
    tools.append(FunctionTool.from_function(
        web_fetch,
        name="web_fetch",
        description="Fetch content from a web URL",
        category=ToolCategory.SEARCH
    ))
    tools.append(FunctionTool.from_function(
        intranet_search,
        name="intranet_search",
        description="Search internal/intranet resources",
        category=ToolCategory.SEARCH
    ))
    tools.append(FunctionTool.from_function(
        news_search,
        name="news_search",
        description="Search news articles by query",
        category=ToolCategory.SEARCH
    ))
    
    # Document handling tools
    tools.append(FunctionTool.from_function(
        read_document,
        name="read_document",
        description="Read and extract content from documents (txt, md, json, csv, etc.)",
        category=ToolCategory.FILE
    ))
    tools.append(FunctionTool.from_function(
        write_document,
        name="write_document",
        description="Write content to a document file",
        category=ToolCategory.FILE
    ))
    tools.append(FunctionTool.from_function(
        convert_document,
        name="convert_document",
        description="Convert document between formats",
        category=ToolCategory.FILE
    ))
    tools.append(FunctionTool.from_function(
        extract_document_metadata,
        name="extract_document_metadata",
        description="Extract metadata from a document file",
        category=ToolCategory.FILE
    ))
    
    # File operation tools
    tools.append(FunctionTool.from_function(
        list_files,
        name="list_files",
        description="List files in a directory with optional pattern matching",
        category=ToolCategory.FILE
    ))
    tools.append(FunctionTool.from_function(
        copy_file,
        name="copy_file",
        description="Copy a file to a new location",
        category=ToolCategory.FILE
    ))
    tools.append(FunctionTool.from_function(
        move_file,
        name="move_file",
        description="Move a file to a new location",
        category=ToolCategory.FILE
    ))
    tools.append(FunctionTool.from_function(
        delete_file,
        name="delete_file",
        description="Delete a file (requires confirmation)",
        category=ToolCategory.FILE
    ))
    
    # System utilities
    tools.append(FunctionTool.from_function(
        get_system_info,
        name="get_system_info",
        description="Get system information including OS, memory, and disk usage",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        execute_shell_command,
        name="execute_shell_command",
        description="Execute a shell command safely with timeout",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        get_environment_variable,
        name="get_environment_variable",
        description="Get an environment variable value",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        set_environment_variable,
        name="set_environment_variable",
        description="Set an environment variable for current process",
        category=ToolCategory.UTILITY
    ))
    
    # Network tools
    tools.append(FunctionTool.from_function(
        check_url_status,
        name="check_url_status",
        description="Check the status and response time of a URL",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        ping_host,
        name="ping_host",
        description="Ping a host to check network connectivity",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        dns_lookup,
        name="dns_lookup",
        description="Perform DNS lookup for a hostname",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        parse_url,
        name="parse_url",
        description="Parse a URL into its components",
        category=ToolCategory.UTILITY
    ))
    
    # Encoding tools
    tools.append(FunctionTool.from_function(
        url_encode,
        name="url_encode",
        description="URL encode a string",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        url_decode,
        name="url_decode",
        description="URL decode a string",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        html_encode,
        name="html_encode",
        description="HTML encode special characters",
        category=ToolCategory.UTILITY
    ))
    tools.append(FunctionTool.from_function(
        html_decode,
        name="html_decode",
        description="HTML decode special characters",
        category=ToolCategory.UTILITY
    ))
    
    return tools


def register_general_tools(registry) -> int:
    """Register all general-purpose tools."""
    tools = get_general_tools()
    count = 0
    for tool in tools:
        if tool.metadata:
            tool.metadata.source = f"prebuilt:general:{tool.name}"
        if registry.register(tool):
            count += 1
    logger.info(f"Registered {count} general-purpose tools")
    return count
