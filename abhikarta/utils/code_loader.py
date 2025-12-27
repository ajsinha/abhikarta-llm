"""
Code Loader Module - Load Python code fragments from various sources.

Supports loading from:
- db://<fragment_id> - Load from database code_fragments table
- file://<file_path> - Load from local filesystem
- s3://<bucket>/<key> - Load from AWS S3

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.
"""

import logging
import os
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class CodeLoader:
    """
    Load Python code fragments from various URI sources.
    
    Supported URI schemes:
    - db://<fragment_id> - Database code_fragments table
    - file://<path> - Local filesystem
    - s3://<bucket>/<key> - AWS S3 bucket
    
    Example:
        loader = CodeLoader(db_facade)
        code = loader.load("db://data-utils")
        code = loader.load("file:///path/to/module.py")
        code = loader.load("s3://my-bucket/code/utils.py")
    """
    
    def __init__(self, db_facade=None, s3_client=None, base_path: str = None):
        """
        Initialize CodeLoader.
        
        Args:
            db_facade: Database facade for db:// URIs
            s3_client: boto3 S3 client for s3:// URIs
            base_path: Base path for relative file:// URIs
        """
        self.db_facade = db_facade
        self.s3_client = s3_client
        self.base_path = base_path or os.getcwd()
        self._cache: Dict[str, str] = {}
        self._cache_enabled = True
    
    def load(self, uri: str, use_cache: bool = True) -> Optional[str]:
        """
        Load code from a URI.
        
        Args:
            uri: URI to load code from (db://, file://, s3://)
            use_cache: Whether to use cached results
            
        Returns:
            Python code as string, or None if not found
        """
        if not uri:
            return None
        
        # Check cache first
        if use_cache and self._cache_enabled and uri in self._cache:
            logger.debug(f"Cache hit for URI: {uri}")
            return self._cache[uri]
        
        # Parse URI scheme
        parsed = urlparse(uri)
        scheme = parsed.scheme.lower()
        
        try:
            if scheme == 'db':
                code = self._load_from_db(parsed.netloc or parsed.path.lstrip('/'))
            elif scheme == 'file':
                code = self._load_from_file(parsed.path)
            elif scheme == 's3':
                code = self._load_from_s3(parsed.netloc, parsed.path.lstrip('/'))
            elif not scheme:
                # No scheme - treat as inline code or fragment_id
                if '\n' in uri or 'def ' in uri or 'import ' in uri:
                    # Looks like inline code
                    code = uri
                else:
                    # Treat as fragment_id
                    code = self._load_from_db(uri)
            else:
                logger.error(f"Unsupported URI scheme: {scheme}")
                return None
            
            # Cache the result
            if code and use_cache and self._cache_enabled:
                self._cache[uri] = code
            
            return code
            
        except Exception as e:
            logger.error(f"Error loading code from URI {uri}: {e}")
            return None
    
    def _load_from_db(self, fragment_id: str) -> Optional[str]:
        """
        Load code from database code_fragments table.
        
        Args:
            fragment_id: The fragment identifier
            
        Returns:
            Code string or None
        """
        if not self.db_facade:
            logger.error("Database facade not configured for db:// URIs")
            return None
        
        try:
            result = self.db_facade.fetch_one(
                """SELECT code FROM code_fragments 
                   WHERE fragment_id = ? AND is_active = 1""",
                (fragment_id,)
            )
            
            if result:
                # Update usage count
                self.db_facade.execute(
                    "UPDATE code_fragments SET usage_count = usage_count + 1 WHERE fragment_id = ?",
                    (fragment_id,)
                )
                return result['code']
            
            logger.warning(f"Code fragment not found: {fragment_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading from database: {e}")
            return None
    
    def _load_from_file(self, file_path: str) -> Optional[str]:
        """
        Load code from local filesystem.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Code string or None
        """
        # Handle relative paths
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.base_path, file_path)
        
        # Security check - prevent path traversal
        real_path = os.path.realpath(file_path)
        if not real_path.startswith(os.path.realpath(self.base_path)):
            logger.error(f"Security: Path traversal detected for {file_path}")
            return None
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def _load_from_s3(self, bucket: str, key: str) -> Optional[str]:
        """
        Load code from AWS S3.
        
        Args:
            bucket: S3 bucket name
            key: Object key (path within bucket)
            
        Returns:
            Code string or None
        """
        if not self.s3_client:
            # Try to create S3 client
            try:
                import boto3
                self.s3_client = boto3.client('s3')
            except ImportError:
                logger.error("boto3 not installed. Install with: pip install boto3")
                return None
            except Exception as e:
                logger.error(f"Failed to create S3 client: {e}")
                return None
        
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            code = response['Body'].read().decode('utf-8')
            return code
            
        except self.s3_client.exceptions.NoSuchKey:
            logger.warning(f"S3 object not found: s3://{bucket}/{key}")
            return None
        except Exception as e:
            logger.error(f"Error loading from S3 s3://{bucket}/{key}: {e}")
            return None
    
    def load_multiple(self, uris: Dict[str, str]) -> Dict[str, str]:
        """
        Load multiple code fragments.
        
        Args:
            uris: Dictionary mapping module names to URIs
            
        Returns:
            Dictionary mapping module names to code
        """
        result = {}
        for name, uri in uris.items():
            code = self.load(uri)
            if code:
                result[name] = code
            else:
                logger.warning(f"Failed to load module {name} from {uri}")
        return result
    
    def resolve_uri(self, uri_or_code: str) -> str:
        """
        Resolve a URI or return inline code as-is.
        
        Args:
            uri_or_code: Either a URI string or inline code
            
        Returns:
            Resolved code string
        """
        # Check if it looks like a URI
        if uri_or_code.startswith(('db://', 'file://', 's3://')):
            return self.load(uri_or_code) or ''
        
        # Check if it's a short fragment reference (no scheme, no newlines)
        if not '\n' in uri_or_code and not ' ' in uri_or_code.strip():
            # Could be a fragment_id - try to load
            code = self._load_from_db(uri_or_code)
            if code:
                return code
        
        # Return as inline code
        return uri_or_code
    
    def clear_cache(self):
        """Clear the code cache."""
        self._cache.clear()
    
    def set_cache_enabled(self, enabled: bool):
        """Enable or disable caching."""
        self._cache_enabled = enabled
        if not enabled:
            self._cache.clear()


def get_code_loader(db_facade=None) -> CodeLoader:
    """
    Get a configured CodeLoader instance.
    
    Args:
        db_facade: Optional database facade
        
    Returns:
        Configured CodeLoader instance
    """
    if db_facade is None:
        try:
            from abhikarta.database import get_db_facade
            db_facade = get_db_facade()
        except Exception:
            pass
    
    return CodeLoader(
        db_facade=db_facade,
        base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
