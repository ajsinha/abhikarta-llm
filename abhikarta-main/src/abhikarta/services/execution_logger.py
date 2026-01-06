"""
Execution Logger - Comprehensive logging for workflow, agent, swarm, and AI org executions.

Creates detailed log files for each execution to aid in debugging and traceability.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha

Version: 1.5.3
"""

import json
import logging
import os
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
import threading

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of entities that can be executed."""
    WORKFLOW = "workflow"
    AGENT = "agent"
    SWARM = "swarm"
    AIORG = "aiorg"


class LogFormat(Enum):
    """Log file formats."""
    JSON = "json"
    TEXT = "text"


@dataclass
class ExecutionLogConfig:
    """Configuration for execution logging."""
    enabled: bool = True
    base_path: str = "executionlog"
    log_format: LogFormat = LogFormat.JSON
    include_llm_responses: bool = True
    file_retention_days: int = 10  # File system log retention
    db_retention_days: int = 30    # Database log retention
    cleanup_interval_hours: int = 24  # How often to run cleanup
    
    # Backward compatibility
    @property
    def retention_days(self) -> int:
        return self.file_retention_days
    
    @classmethod
    def from_properties(cls, prop_conf) -> 'ExecutionLogConfig':
        """Load configuration from PropertiesConfigurator."""
        config = cls()
        
        if prop_conf:
            config.enabled = prop_conf.get('execution.log.enabled', 'true').lower() == 'true'
            config.base_path = prop_conf.get('execution.log.path', 'executionlog')
            
            format_str = prop_conf.get('execution.log.format', 'json').lower()
            config.log_format = LogFormat.JSON if format_str == 'json' else LogFormat.TEXT
            
            config.include_llm_responses = prop_conf.get(
                'execution.log.include.llm.responses', 'true'
            ).lower() == 'true'
            
            # New separate retention settings
            try:
                config.file_retention_days = int(prop_conf.get(
                    'execution.log.file.retention.days', 
                    prop_conf.get('execution.log.retention.days', '10')  # Fallback to old setting
                ))
            except ValueError:
                config.file_retention_days = 10
            
            try:
                config.db_retention_days = int(prop_conf.get('execution.log.db.retention.days', '30'))
            except ValueError:
                config.db_retention_days = 30
            
            try:
                config.cleanup_interval_hours = int(prop_conf.get('execution.log.cleanup.interval.hours', '24'))
            except ValueError:
                config.cleanup_interval_hours = 24
        
        return config


@dataclass
class ExecutionLogEntry:
    """A single log entry within an execution."""
    timestamp: str
    level: str
    message: str
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'timestamp': self.timestamp,
            'level': self.level,
            'message': self.message
        }
        if self.data:
            result['data'] = self.data
        return result


@dataclass
class ExecutionLog:
    """Complete execution log for a single execution."""
    execution_id: str
    entity_type: EntityType
    entity_id: str
    entity_name: str
    started_at: str
    user_id: Optional[str] = None
    
    # Input and configuration
    user_input: Optional[Dict[str, Any]] = None
    entity_config: Optional[Dict[str, Any]] = None
    llm_config: Optional[Dict[str, Any]] = None
    environment_config: Optional[Dict[str, Any]] = None
    
    # Execution details
    execution_json: Optional[Dict[str, Any]] = None
    execution_python: Optional[str] = None
    
    # Results
    completed_at: Optional[str] = None
    status: str = "running"
    output: Optional[Any] = None
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    
    # Log entries
    entries: List[ExecutionLogEntry] = field(default_factory=list)
    
    # Node/Step execution details
    node_executions: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_entry(self, level: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Add a log entry."""
        entry = ExecutionLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            message=message,
            data=data
        )
        self.entries.append(entry)
    
    def add_node_execution(self, node_id: str, node_type: str, 
                          input_data: Any = None, output_data: Any = None,
                          duration_ms: float = None, error: str = None):
        """Add a node/step execution record."""
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'node_id': node_id,
            'node_type': node_type,
            'input': input_data,
            'output': output_data,
            'duration_ms': duration_ms,
            'error': error
        }
        self.node_executions.append(record)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'execution_id': self.execution_id,
            'entity_type': self.entity_type.value,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'user_id': self.user_id,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'status': self.status,
            'user_input': self.user_input,
            'entity_config': self.entity_config,
            'llm_config': self.llm_config,
            'environment_config': self.environment_config,
            'execution_json': self.execution_json,
            'execution_python': self.execution_python,
            'output': self.output,
            'error': self.error,
            'error_traceback': self.error_traceback,
            'entries': [e.to_dict() for e in self.entries],
            'node_executions': self.node_executions
        }
    
    def to_text(self) -> str:
        """Convert to human-readable text format."""
        lines = [
            "=" * 80,
            f"EXECUTION LOG: {self.execution_id}",
            "=" * 80,
            "",
            "METADATA",
            "-" * 40,
            f"Entity Type: {self.entity_type.value}",
            f"Entity ID: {self.entity_id}",
            f"Entity Name: {self.entity_name}",
            f"User ID: {self.user_id or 'N/A'}",
            f"Started: {self.started_at}",
            f"Completed: {self.completed_at or 'N/A'}",
            f"Status: {self.status}",
            "",
            "USER INPUT",
            "-" * 40,
            json.dumps(self.user_input, indent=2) if self.user_input else "None",
            "",
            "ENTITY CONFIGURATION",
            "-" * 40,
            json.dumps(self.entity_config, indent=2) if self.entity_config else "None",
            "",
            "LLM CONFIGURATION",
            "-" * 40,
            json.dumps(self.llm_config, indent=2) if self.llm_config else "None",
            "",
            "ENVIRONMENT CONFIGURATION",
            "-" * 40,
            json.dumps(self.environment_config, indent=2) if self.environment_config else "None",
            "",
        ]
        
        if self.execution_json:
            lines.extend([
                "EXECUTION JSON",
                "-" * 40,
                json.dumps(self.execution_json, indent=2),
                ""
            ])
        
        if self.execution_python:
            lines.extend([
                "EXECUTION PYTHON",
                "-" * 40,
                self.execution_python,
                ""
            ])
        
        if self.node_executions:
            lines.extend([
                "NODE EXECUTIONS",
                "-" * 40
            ])
            for i, node in enumerate(self.node_executions):
                lines.append(f"\n[{i+1}] {node.get('node_id')} ({node.get('node_type')})")
                lines.append(f"    Time: {node.get('timestamp')}")
                if node.get('duration_ms'):
                    lines.append(f"    Duration: {node.get('duration_ms'):.2f}ms")
                if node.get('input'):
                    lines.append(f"    Input: {json.dumps(node.get('input'))[:200]}...")
                if node.get('output'):
                    lines.append(f"    Output: {json.dumps(node.get('output'))[:200]}...")
                if node.get('error'):
                    lines.append(f"    ERROR: {node.get('error')}")
            lines.append("")
        
        if self.entries:
            lines.extend([
                "LOG ENTRIES",
                "-" * 40
            ])
            for entry in self.entries:
                lines.append(f"[{entry.timestamp}] [{entry.level}] {entry.message}")
                if entry.data:
                    lines.append(f"    Data: {json.dumps(entry.data)[:200]}...")
            lines.append("")
        
        if self.output:
            lines.extend([
                "OUTPUT",
                "-" * 40,
                json.dumps(self.output, indent=2) if isinstance(self.output, (dict, list)) else str(self.output),
                ""
            ])
        
        if self.error:
            lines.extend([
                "ERROR",
                "-" * 40,
                self.error,
                "",
                "TRACEBACK",
                "-" * 40,
                self.error_traceback or "N/A",
                ""
            ])
        
        lines.append("=" * 80)
        return "\n".join(lines)


class ExecutionLogger:
    """
    Service for logging execution details to files.
    
    Creates and manages execution logs for workflows, agents, swarms, and AI orgs.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, config: ExecutionLogConfig = None):
        """Singleton pattern for ExecutionLogger."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: ExecutionLogConfig = None):
        """Initialize the ExecutionLogger."""
        if self._initialized:
            return
        
        self.config = config or ExecutionLogConfig()
        
        # Convert base_path to absolute path for consistency
        if not os.path.isabs(self.config.base_path):
            self.config.base_path = os.path.abspath(self.config.base_path)
        
        self._active_logs: Dict[str, ExecutionLog] = {}
        self._file_lock = threading.Lock()
        
        # Initialize directories
        if self.config.enabled:
            self._init_directories()
        
        self._initialized = True
        logger.info(f"ExecutionLogger initialized: enabled={self.config.enabled}, path={self.config.base_path}")
    
    def _init_directories(self):
        """Create the directory structure for execution logs."""
        base_path = Path(self.config.base_path)
        
        # Create base directory and entity type subdirectories
        for entity_type in EntityType:
            dir_path = base_path / entity_type.value
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created/verified log directory: {dir_path}")
    
    def _get_log_path(self, entity_type: EntityType, execution_id: str) -> Path:
        """Get the path for a log file."""
        base_path = Path(self.config.base_path)
        extension = "json" if self.config.log_format == LogFormat.JSON else "log"
        return base_path / entity_type.value / f"{execution_id}.{extension}"
    
    def start_execution(self, 
                       execution_id: str,
                       entity_type: EntityType,
                       entity_id: str,
                       entity_name: str,
                       user_id: str = None,
                       user_input: Dict[str, Any] = None,
                       entity_config: Dict[str, Any] = None,
                       llm_config: Dict[str, Any] = None,
                       environment_config: Dict[str, Any] = None,
                       execution_json: Dict[str, Any] = None,
                       execution_python: str = None) -> ExecutionLog:
        """
        Start logging a new execution.
        
        Args:
            execution_id: Unique execution identifier
            entity_type: Type of entity (workflow, agent, swarm, aiorg)
            entity_id: ID of the entity being executed
            entity_name: Name of the entity
            user_id: ID of the user who initiated execution
            user_input: Input provided by the user
            entity_config: Configuration of the entity
            llm_config: LLM configuration being used
            environment_config: Environment/system configuration
            execution_json: JSON definition being executed
            execution_python: Python code being executed
            
        Returns:
            ExecutionLog object for continued logging
        """
        if not self.config.enabled:
            # Return a dummy log that won't be saved
            return ExecutionLog(
                execution_id=execution_id,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name,
                started_at=datetime.now(timezone.utc).isoformat()
            )
        
        log = ExecutionLog(
            execution_id=execution_id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            user_id=user_id,
            started_at=datetime.now(timezone.utc).isoformat(),
            user_input=user_input,
            entity_config=entity_config,
            llm_config=llm_config,
            environment_config=environment_config,
            execution_json=execution_json,
            execution_python=execution_python
        )
        
        log.add_entry("INFO", f"Execution started for {entity_type.value}: {entity_name}")
        
        self._active_logs[execution_id] = log
        
        # Write initial log file
        self._write_log(log)
        
        logger.info(f"Started execution log: {execution_id} ({entity_type.value})")
        return log
    
    def log_entry(self, execution_id: str, level: str, message: str, 
                  data: Dict[str, Any] = None):
        """Add a log entry to an active execution."""
        if not self.config.enabled:
            return
        
        log = self._active_logs.get(execution_id)
        if log:
            log.add_entry(level, message, data)
            self._write_log(log)
    
    def log_node_execution(self, execution_id: str, node_id: str, node_type: str,
                          input_data: Any = None, output_data: Any = None,
                          duration_ms: float = None, error: str = None):
        """Log a node/step execution within a workflow or agent."""
        if not self.config.enabled:
            return
        
        log = self._active_logs.get(execution_id)
        if log:
            # Optionally truncate large LLM responses
            if not self.config.include_llm_responses and node_type == 'llm':
                if isinstance(output_data, dict):
                    output_data = {k: v[:100] + '...' if isinstance(v, str) and len(v) > 100 else v 
                                  for k, v in output_data.items()}
                elif isinstance(output_data, str) and len(output_data) > 100:
                    output_data = output_data[:100] + '...'
            
            log.add_node_execution(node_id, node_type, input_data, output_data, 
                                  duration_ms, error)
            self._write_log(log)
    
    def log_llm_call(self, execution_id: str, provider: str, model: str,
                    prompt: str, response: str = None, error: str = None,
                    duration_ms: float = None, tokens_used: int = None):
        """Log an LLM API call."""
        if not self.config.enabled:
            return
        
        log = self._active_logs.get(execution_id)
        if log:
            data = {
                'provider': provider,
                'model': model,
                'prompt_length': len(prompt) if prompt else 0,
                'duration_ms': duration_ms,
                'tokens_used': tokens_used
            }
            
            if self.config.include_llm_responses:
                data['prompt'] = prompt
                data['response'] = response
            else:
                data['response_length'] = len(response) if response else 0
            
            if error:
                data['error'] = error
                log.add_entry("ERROR", f"LLM call failed: {provider}/{model}", data)
            else:
                log.add_entry("INFO", f"LLM call completed: {provider}/{model}", data)
            
            self._write_log(log)
    
    def complete_execution(self, execution_id: str, status: str = "completed",
                          output: Any = None, error: str = None,
                          error_traceback: str = None):
        """
        Mark an execution as complete and finalize the log.
        
        Args:
            execution_id: Execution to complete
            status: Final status (completed, failed, cancelled)
            output: Execution output/result
            error: Error message if failed
            error_traceback: Full traceback if failed
        """
        if not self.config.enabled:
            return
        
        log = self._active_logs.get(execution_id)
        if log:
            log.completed_at = datetime.now(timezone.utc).isoformat()
            log.status = status
            log.output = output
            log.error = error
            log.error_traceback = error_traceback
            
            log.add_entry("INFO" if status == "completed" else "ERROR",
                         f"Execution {status}: {log.entity_name}")
            
            # Write final log
            self._write_log(log)
            
            # Remove from active logs
            del self._active_logs[execution_id]
            
            logger.info(f"Completed execution log: {execution_id} ({status})")
    
    def _write_log(self, log: ExecutionLog):
        """Write log to file."""
        if not self.config.enabled:
            return
        
        try:
            with self._file_lock:
                log_path = self._get_log_path(log.entity_type, log.execution_id)
                
                # Ensure directory exists
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                if self.config.log_format == LogFormat.JSON:
                    content = json.dumps(log.to_dict(), indent=2, default=str)
                else:
                    content = log.to_text()
                
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            logger.error(f"Failed to write execution log {log.execution_id}: {e}")
    
    def get_log(self, execution_id: str) -> Optional[ExecutionLog]:
        """Get an active execution log."""
        return self._active_logs.get(execution_id)
    
    def get_log_path(self, entity_type: EntityType, execution_id: str) -> Path:
        """Get the file path for an execution log."""
        return self._get_log_path(entity_type, execution_id)
    
    def detect_entity_type_from_id(self, execution_id: str) -> Optional[EntityType]:
        """
        Detect entity type from execution ID if it uses the traceable format.
        
        Format: <type>_<name>_<uuid> or <type>_<uuid>
        Prefixes: wflow=workflow, agent=agent, swarm=swarm, aiorg=aiorg
        
        Args:
            execution_id: Execution ID to parse
            
        Returns:
            EntityType if detected, None otherwise
        """
        if not execution_id:
            return None
        
        prefix = execution_id.split('_')[0] if '_' in execution_id else None
        
        type_map = {
            'wflow': EntityType.WORKFLOW,
            'agent': EntityType.AGENT,
            'swarm': EntityType.SWARM,
            'aiorg': EntityType.AIORG,
        }
        
        return type_map.get(prefix)
    
    def find_log_file(self, execution_id: str) -> Optional[Tuple[EntityType, Path]]:
        """
        Find a log file by execution ID, auto-detecting entity type if possible.
        
        First tries to detect entity type from execution ID format.
        If that fails, searches all entity type directories.
        
        Args:
            execution_id: Execution ID to find
            
        Returns:
            Tuple of (EntityType, Path) if found, None otherwise
        """
        # Try to detect from execution ID format
        detected_type = self.detect_entity_type_from_id(execution_id)
        if detected_type:
            log_path = self._get_log_path(detected_type, execution_id)
            if log_path.exists():
                return (detected_type, log_path)
        
        # Search all entity type directories
        for entity_type in EntityType:
            log_path = self._get_log_path(entity_type, execution_id)
            if log_path.exists():
                return (entity_type, log_path)
        
        return None
    
    def read_log_file(self, entity_type: EntityType, execution_id: str) -> Optional[Dict[str, Any]]:
        """Read a log file from disk."""
        log_path = self._get_log_path(entity_type, execution_id)
        
        if not log_path.exists():
            return None
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                if self.config.log_format == LogFormat.JSON:
                    return json.load(f)
                else:
                    return {'content': f.read()}
        except Exception as e:
            logger.error(f"Failed to read log file {log_path}: {e}")
            return None
    
    def read_log_file_auto(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a log file, auto-detecting entity type from execution ID.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Log data dict if found, None otherwise
        """
        result = self.find_log_file(execution_id)
        if result:
            entity_type, log_path = result
            return self.read_log_file(entity_type, execution_id)
        return None
    
    def list_logs(self, entity_type: EntityType, limit: int = 100) -> List[Dict[str, Any]]:
        """List recent execution logs for an entity type."""
        base_path = Path(self.config.base_path) / entity_type.value
        
        if not base_path.exists():
            return []
        
        logs = []
        extension = ".json" if self.config.log_format == LogFormat.JSON else ".log"
        
        # Get files sorted by modification time (newest first)
        files = sorted(base_path.glob(f"*{extension}"), 
                      key=lambda x: x.stat().st_mtime, reverse=True)
        
        for log_file in files[:limit]:
            execution_id = log_file.stem
            stat = log_file.stat()
            logs.append({
                'execution_id': execution_id,
                'entity_type': entity_type.value,
                'file_path': str(log_file),
                'size_bytes': stat.st_size,
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return logs
    
    def cleanup_old_logs(self, db_facade=None):
        """Remove logs older than retention period (both files and database)."""
        file_count = self._cleanup_old_log_files()
        db_count = self._cleanup_old_db_logs(db_facade) if db_facade else 0
        
        if file_count > 0 or db_count > 0:
            logger.info(f"Execution log cleanup: removed {file_count} files, {db_count} database records")
        
        return file_count, db_count
    
    def _cleanup_old_log_files(self) -> int:
        """Remove log files older than file retention period."""
        if self.config.file_retention_days <= 0:
            return 0  # Keep forever
        
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=self.config.file_retention_days)
        
        removed_count = 0
        base_path = Path(self.config.base_path)
        
        for entity_type in EntityType:
            dir_path = base_path / entity_type.value
            if not dir_path.exists():
                continue
            
            for log_file in dir_path.glob("*"):
                try:
                    if log_file.stat().st_mtime < cutoff.timestamp():
                        log_file.unlink()
                        removed_count += 1
                except Exception as e:
                    logger.error(f"Failed to remove old log {log_file}: {e}")
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old execution log files")
        
        return removed_count
    
    def _cleanup_old_db_logs(self, db_facade) -> int:
        """Remove database execution records older than DB retention period."""
        if self.config.db_retention_days <= 0 or not db_facade:
            return 0  # Keep forever or no DB access
        
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=self.config.db_retention_days)
        cutoff_str = cutoff.isoformat()
        
        removed_count = 0
        
        # Tables to clean up with possible date column names
        # Try multiple column names for each table for compatibility
        # Order: preferred column first, then fallbacks for older schemas
        tables = [
            ('executions', ['started_at', 'created_at']),
            ('agent_executions', ['started_at', 'created_at']),
            ('swarm_executions', ['started_at', 'created_at', 'start_time']),
        ]
        
        for table, date_columns in tables:
            # First check if table exists
            try:
                table_check = db_facade.fetch_one(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table,)
                )
                if not table_check:
                    continue  # Table doesn't exist, skip
            except Exception:
                continue  # Error checking table, skip
            
            # Try each possible date column
            for date_column in date_columns:
                try:
                    # Check if column exists by trying a simple query
                    result = db_facade.fetch_one(
                        f"SELECT COUNT(*) as cnt FROM {table} WHERE {date_column} < ?",
                        (cutoff_str,)
                    )
                    if result:
                        count = result.get('cnt', 0) if isinstance(result, dict) else result[0]
                        if count > 0:
                            db_facade.execute(
                                f"DELETE FROM {table} WHERE {date_column} < ?",
                                (cutoff_str,)
                            )
                            removed_count += count
                            logger.info(f"Cleaned up {count} old records from {table}")
                    break  # Column found and processed, move to next table
                except Exception as e:
                    # Column doesn't exist, try next one
                    logger.debug(f"Column {date_column} not found in {table}: {e}")
                    continue
        
        return removed_count


# Singleton accessor functions
_default_logger: Optional[ExecutionLogger] = None


def get_execution_logger() -> ExecutionLogger:
    """Get the default ExecutionLogger instance."""
    global _default_logger
    if _default_logger is None:
        _default_logger = ExecutionLogger()
    return _default_logger


def init_execution_logger(config: ExecutionLogConfig = None) -> ExecutionLogger:
    """Initialize the default ExecutionLogger with configuration."""
    global _default_logger
    _default_logger = ExecutionLogger(config)
    return _default_logger


def init_execution_logger_from_properties(prop_conf) -> ExecutionLogger:
    """Initialize ExecutionLogger from PropertiesConfigurator."""
    config = ExecutionLogConfig.from_properties(prop_conf)
    return init_execution_logger(config)
