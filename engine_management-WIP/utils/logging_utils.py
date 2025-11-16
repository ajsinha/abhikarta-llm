"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    format_string: str = None
) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        format_string: Custom format string
    
    Returns:
        Configured logger
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers
    )
    
    return logging.getLogger("abhikarta")

class ExecutionLogger:
    """Structured logging for execution tracking"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = logging.getLogger(f"execution.{session_id}")
    
    def log_start(self, mode: str, user_id: str):
        """Log execution start"""
        self.logger.info(
            f"Starting {mode} execution",
            extra={
                "session_id": self.session_id,
                "user_id": user_id,
                "mode": mode,
                "event": "start"
            }
        )
    
    def log_step(self, step: str, details: dict = None):
        """Log execution step"""
        self.logger.info(
            f"Executing step: {step}",
            extra={
                "session_id": self.session_id,
                "step": step,
                "details": details or {},
                "event": "step"
            }
        )
    
    def log_tool_call(self, tool_name: str, inputs: dict):
        """Log tool invocation"""
        self.logger.debug(
            f"Calling tool: {tool_name}",
            extra={
                "session_id": self.session_id,
                "tool": tool_name,
                "inputs": inputs,
                "event": "tool_call"
            }
        )
    
    def log_error(self, error: str, error_type: str = None):
        """Log error"""
        self.logger.error(
            f"Execution error: {error}",
            extra={
                "session_id": self.session_id,
                "error": error,
                "error_type": error_type,
                "event": "error"
            }
        )
    
    def log_completion(self, status: str, duration_ms: float = None):
        """Log execution completion"""
        self.logger.info(
            f"Execution completed with status: {status}",
            extra={
                "session_id": self.session_id,
                "status": status,
                "duration_ms": duration_ms,
                "event": "completion"
            }
        )
