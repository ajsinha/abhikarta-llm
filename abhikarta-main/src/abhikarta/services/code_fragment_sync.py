"""
Code Fragment Sync Service - Syncs approved code fragments to local Python modules.

This service:
1. Creates a captive code_fragments module folder
2. Syncs approved/published fragments as Python modules
3. Adds the folder to sys.path for standard imports
4. Watches for changes and hot-reloads modules
5. Handles dependencies between fragments

Usage in workflows/agents:
    from code_fragments.data_validator import validate_email
    from code_fragments.csv_parser import parse_csv

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.5.1
"""

import os
import sys
import time
import hashlib
import importlib
import importlib.util
import threading
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Sync status for a fragment."""
    PENDING = "pending"
    SYNCED = "synced"
    ERROR = "error"
    DELETED = "deleted"


@dataclass
class SyncConfig:
    """Configuration for code fragment sync."""
    # Base path for code_fragments module
    target_path: str = ""
    
    # Sync interval in seconds (default 5 minutes)
    sync_interval_seconds: int = 300
    
    # Sync on startup
    sync_on_startup: bool = True
    
    # Watch for changes
    watch_enabled: bool = True
    
    # Status filter for syncing
    status_filter: List[str] = field(default_factory=lambda: ["approved", "published"])
    
    # Language filter (only Python fragments can be synced as modules)
    language_filter: str = "python"
    
    # Reload strategy: 'graceful' waits for running executions, 'immediate' reloads now
    reload_strategy: str = "graceful"
    
    # Max wait time for graceful reload
    max_wait_seconds: int = 30
    
    # Enable S3 source
    s3_enabled: bool = False
    s3_bucket: str = ""
    s3_prefix: str = ""
    
    # Enable filesystem source
    filesystem_enabled: bool = False
    filesystem_paths: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.target_path:
            # Default to project root / code_fragments
            self.target_path = os.path.join(os.getcwd(), "code_fragments")


@dataclass
class FragmentSyncInfo:
    """Sync information for a single fragment."""
    fragment_id: str
    module_name: str
    name: str
    checksum: str
    file_path: str
    status: SyncStatus
    synced_at: Optional[datetime] = None
    error: Optional[str] = None


class CodeFragmentSyncService:
    """
    Service to sync code fragments from database to local Python modules.
    
    Architecture:
    - Creates: {target_path}/src/code_fragments/
    - Each fragment becomes: {target_path}/src/code_fragments/{module_name}.py
    - Adds {target_path}/src to sys.path
    - Generates __init__.py with all exports
    
    Usage:
        service = CodeFragmentSyncService(db_facade, config)
        service.start()  # Starts sync and watcher
        
        # Later in code:
        from code_fragments.data_validator import validate
    """
    
    def __init__(self, db_facade, config: Optional[SyncConfig] = None):
        """
        Initialize sync service.
        
        Args:
            db_facade: Database facade with code_fragments delegate
            config: Sync configuration (uses defaults if not provided)
        """
        self.db_facade = db_facade
        self.config = config or SyncConfig()
        
        # Paths
        self.target_path = Path(self.config.target_path)
        self.src_path = self.target_path / "src"
        self.module_path = self.src_path / "code_fragments"
        
        # State
        self._synced_fragments: Dict[str, FragmentSyncInfo] = {}
        self._running = False
        self._watch_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._callbacks: List[Callable[[str, SyncStatus], None]] = []
        
        # Statistics
        self._stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_sync_time': None,
            'last_sync_duration': 0,
        }
    
    # ==========================================================================
    # INITIALIZATION
    # ==========================================================================
    
    def initialize(self) -> bool:
        """
        Initialize the sync service.
        Creates directories, sets up Python path.
        
        Returns:
            True if initialization successful
        """
        try:
            # Create directory structure
            self._create_directories()
            
            # Add to Python path
            self._add_to_python_path()
            
            # Initial sync if configured
            if self.config.sync_on_startup:
                self.sync_all()
            
            logger.info(f"CodeFragmentSyncService initialized. Module path: {self.module_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize CodeFragmentSyncService: {e}", exc_info=True)
            return False
    
    def _create_directories(self):
        """Create the directory structure for code_fragments module."""
        # Create main directories
        self.module_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py for src (make it a package)
        src_init = self.src_path / "__init__.py"
        if not src_init.exists():
            src_init.write_text("# Auto-generated by CodeFragmentSyncService\n")
        
        # Create __init__.py for code_fragments
        self._generate_init_file()
        
        logger.debug(f"Created directory structure at {self.target_path}")
    
    def _add_to_python_path(self):
        """Add the src directory to Python path for imports."""
        src_path_str = str(self.src_path)
        if src_path_str not in sys.path:
            sys.path.insert(0, src_path_str)
            logger.info(f"Added {src_path_str} to sys.path")
    
    def _generate_init_file(self):
        """Generate __init__.py with all module exports."""
        with self._lock:
            init_path = self.module_path / "__init__.py"
            
            # Get all synced modules
            module_names = sorted([
                info.module_name for info in self._synced_fragments.values()
                if info.status == SyncStatus.SYNCED
            ])
            
            # Also check filesystem for any .py files
            if self.module_path.exists():
                for py_file in self.module_path.glob("*.py"):
                    if py_file.name != "__init__.py":
                        mod_name = py_file.stem
                        if mod_name not in module_names:
                            module_names.append(mod_name)
                module_names = sorted(set(module_names))
            
            # Generate init content
            lines = [
                '"""',
                'Code Fragments Module - Auto-generated by CodeFragmentSyncService',
                '',
                'This module contains approved code fragments synced from the database.',
                'Do not edit this file directly - changes will be overwritten.',
                '',
                f'Last updated: {datetime.now().isoformat()}',
                f'Total fragments: {len(module_names)}',
                '"""',
                '',
                '# Available fragments:',
            ]
            
            for mod_name in module_names:
                lines.append(f'# - {mod_name}')
            
            lines.extend([
                '',
                '__all__ = [',
            ])
            
            for mod_name in module_names:
                lines.append(f'    "{mod_name}",')
            
            lines.extend([
                ']',
                '',
                '# Import all fragments for convenience',
            ])
            
            for mod_name in module_names:
                lines.append(f'from . import {mod_name}')
            
            lines.append('')
            
            # Write atomically
            self._atomic_write(init_path, '\n'.join(lines))
    
    # ==========================================================================
    # SYNC OPERATIONS
    # ==========================================================================
    
    def sync_all(self) -> Dict[str, Any]:
        """
        Sync all approved/published fragments from database.
        
        Returns:
            Summary of sync operation
        """
        start_time = time.time()
        results = {
            'synced': [],
            'failed': [],
            'removed': [],
            'unchanged': [],
        }
        
        try:
            # Get syncable fragments from database
            fragments = self.db_facade.code_fragments.get_syncable_fragments()
            logger.info(f"Found {len(fragments)} syncable fragments")
            
            # Track which fragments exist in DB
            db_module_names: Set[str] = set()
            
            # Sync each fragment
            for fragment in fragments:
                module_name = fragment.get('module_name')
                if not module_name:
                    logger.warning(f"Fragment {fragment.get('fragment_id')} has no module_name, skipping")
                    continue
                
                db_module_names.add(module_name)
                
                result = self._sync_fragment(fragment)
                if result == SyncStatus.SYNCED:
                    results['synced'].append(module_name)
                elif result == SyncStatus.ERROR:
                    results['failed'].append(module_name)
                else:
                    results['unchanged'].append(module_name)
            
            # Remove fragments that are no longer in DB or no longer approved
            with self._lock:
                to_remove = []
                for module_name, info in self._synced_fragments.items():
                    if module_name not in db_module_names:
                        to_remove.append(module_name)
                
                for module_name in to_remove:
                    self._remove_fragment(module_name)
                    results['removed'].append(module_name)
            
            # Regenerate __init__.py
            self._generate_init_file()
            
            # Update stats
            duration = time.time() - start_time
            self._stats['total_syncs'] += 1
            self._stats['successful_syncs'] += len(results['synced'])
            self._stats['failed_syncs'] += len(results['failed'])
            self._stats['last_sync_time'] = datetime.now()
            self._stats['last_sync_duration'] = duration
            
            logger.info(
                f"Sync complete in {duration:.2f}s: "
                f"{len(results['synced'])} synced, "
                f"{len(results['failed'])} failed, "
                f"{len(results['removed'])} removed, "
                f"{len(results['unchanged'])} unchanged"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error during sync_all: {e}", exc_info=True)
            return results
    
    def _sync_fragment(self, fragment: Dict) -> SyncStatus:
        """
        Sync a single fragment to local file.
        
        Args:
            fragment: Fragment data from database
            
        Returns:
            Sync status
        """
        fragment_id = fragment.get('fragment_id')
        module_name = fragment.get('module_name')
        name = fragment.get('name')
        code = fragment.get('code', '')
        db_checksum = fragment.get('checksum', '')
        
        try:
            # Calculate checksum if not in DB
            if not db_checksum:
                db_checksum = hashlib.sha256(code.encode('utf-8')).hexdigest()
            
            # Check if already synced with same checksum
            with self._lock:
                existing = self._synced_fragments.get(module_name)
                if existing and existing.checksum == db_checksum:
                    # No change needed
                    return SyncStatus.SYNCED
            
            # Validate module name
            if not self._is_valid_module_name(module_name):
                error = f"Invalid module name: {module_name}"
                logger.error(error)
                self._update_fragment_sync_status(fragment_id, False, error)
                return SyncStatus.ERROR
            
            # Prepare file path
            file_path = self.module_path / f"{module_name}.py"
            
            # Prepare module content with metadata header
            content = self._prepare_module_content(fragment)
            
            # Write atomically
            self._atomic_write(file_path, content)
            
            # Update tracking
            with self._lock:
                self._synced_fragments[module_name] = FragmentSyncInfo(
                    fragment_id=fragment_id,
                    module_name=module_name,
                    name=name,
                    checksum=db_checksum,
                    file_path=str(file_path),
                    status=SyncStatus.SYNCED,
                    synced_at=datetime.now(),
                )
            
            # Update database sync status
            self._update_fragment_sync_status(fragment_id, True)
            
            # Reload module if already imported
            self._reload_module_if_loaded(module_name)
            
            # Notify callbacks
            self._notify_callbacks(module_name, SyncStatus.SYNCED)
            
            logger.debug(f"Synced fragment: {module_name} ({fragment_id})")
            return SyncStatus.SYNCED
            
        except Exception as e:
            error = str(e)
            logger.error(f"Failed to sync fragment {module_name}: {error}")
            self._update_fragment_sync_status(fragment_id, False, error)
            
            with self._lock:
                if module_name in self._synced_fragments:
                    self._synced_fragments[module_name].status = SyncStatus.ERROR
                    self._synced_fragments[module_name].error = error
            
            return SyncStatus.ERROR
    
    def _prepare_module_content(self, fragment: Dict) -> str:
        """
        Prepare Python module content with metadata header.
        
        Args:
            fragment: Fragment data
            
        Returns:
            Module content string
        """
        name = fragment.get('name', 'Unknown')
        module_name = fragment.get('module_name', '')
        description = fragment.get('description', '')
        version = fragment.get('version', '1.0.0')
        category = fragment.get('category', 'general')
        created_by = fragment.get('created_by', 'Unknown')
        code = fragment.get('code', '')
        entry_point = fragment.get('entry_point', '')
        
        # Build header
        header_lines = [
            '"""',
            f'{name}',
            '',
            f'{description}' if description else 'No description provided.',
            '',
            'Auto-synced by CodeFragmentSyncService - DO NOT EDIT DIRECTLY',
            '',
            f'Module: code_fragments.{module_name}',
            f'Version: {version}',
            f'Category: {category}',
            f'Author: {created_by}',
            f'Synced: {datetime.now().isoformat()}',
        ]
        
        if entry_point:
            header_lines.append(f'Entry Point: {entry_point}')
        
        header_lines.extend(['"""', ''])
        
        # Combine header and code
        header = '\n'.join(header_lines)
        
        # Ensure code doesn't start with redundant docstring
        code_stripped = code.strip()
        if code_stripped.startswith('"""') or code_stripped.startswith("'''"):
            # Code has its own docstring, skip our header docstring
            return code
        
        return header + code
    
    def _remove_fragment(self, module_name: str):
        """Remove a fragment from local storage."""
        try:
            file_path = self.module_path / f"{module_name}.py"
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Removed fragment file: {file_path}")
            
            with self._lock:
                if module_name in self._synced_fragments:
                    del self._synced_fragments[module_name]
            
            # Unload module if loaded
            full_module_name = f"code_fragments.{module_name}"
            if full_module_name in sys.modules:
                del sys.modules[full_module_name]
            
            self._notify_callbacks(module_name, SyncStatus.DELETED)
            
        except Exception as e:
            logger.error(f"Error removing fragment {module_name}: {e}")
    
    # ==========================================================================
    # MODULE RELOAD
    # ==========================================================================
    
    def _reload_module_if_loaded(self, module_name: str):
        """Reload a module if it's already been imported."""
        full_module_name = f"code_fragments.{module_name}"
        
        if full_module_name in sys.modules:
            try:
                if self.config.reload_strategy == "graceful":
                    # For graceful reload, we could implement execution tracking
                    # For now, just reload
                    pass
                
                module = sys.modules[full_module_name]
                importlib.reload(module)
                logger.debug(f"Reloaded module: {full_module_name}")
                
            except Exception as e:
                logger.error(f"Failed to reload module {full_module_name}: {e}")
    
    def reload_all_modules(self):
        """Force reload all synced modules."""
        # First reload the package itself
        if "code_fragments" in sys.modules:
            try:
                importlib.reload(sys.modules["code_fragments"])
            except Exception as e:
                logger.error(f"Failed to reload code_fragments package: {e}")
        
        # Then reload individual modules
        with self._lock:
            for module_name in self._synced_fragments.keys():
                self._reload_module_if_loaded(module_name)
    
    # ==========================================================================
    # WATCHER
    # ==========================================================================
    
    def start(self):
        """Start the sync service and watcher."""
        if self._running:
            logger.warning("CodeFragmentSyncService already running")
            return
        
        self._running = True
        
        # Initialize
        self.initialize()
        
        # Start watcher thread if enabled
        if self.config.watch_enabled and self.config.sync_interval_seconds > 0:
            self._watch_thread = threading.Thread(
                target=self._watch_loop,
                daemon=True,
                name="CodeFragmentSyncWatcher"
            )
            self._watch_thread.start()
            logger.info(
                f"Started CodeFragmentSyncService watcher "
                f"(interval: {self.config.sync_interval_seconds}s)"
            )
    
    def stop(self):
        """Stop the sync service and watcher."""
        self._running = False
        if self._watch_thread:
            self._watch_thread.join(timeout=5)
            self._watch_thread = None
        logger.info("Stopped CodeFragmentSyncService")
    
    def _watch_loop(self):
        """Background loop to periodically check for changes."""
        while self._running:
            try:
                # Sleep first (so startup sync isn't duplicated)
                for _ in range(self.config.sync_interval_seconds):
                    if not self._running:
                        return
                    time.sleep(1)
                
                if not self._running:
                    return
                
                # Check for changes
                self._check_for_changes()
                
            except Exception as e:
                logger.error(f"Error in watch loop: {e}", exc_info=True)
                time.sleep(10)  # Back off on error
    
    def _check_for_changes(self):
        """Check for fragments needing sync."""
        try:
            fragments_needing_sync = self.db_facade.code_fragments.get_fragments_needing_sync()
            
            if fragments_needing_sync:
                logger.info(f"Found {len(fragments_needing_sync)} fragments needing sync")
                for fragment in fragments_needing_sync:
                    self._sync_fragment(fragment)
                
                # Regenerate init after syncing
                self._generate_init_file()
                
        except Exception as e:
            logger.error(f"Error checking for changes: {e}")
    
    # ==========================================================================
    # UTILITIES
    # ==========================================================================
    
    def _atomic_write(self, path: Path, content: str):
        """
        Write file atomically using temp file and rename.
        
        Args:
            path: Target file path
            content: File content
        """
        # Write to temp file in same directory
        temp_fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            suffix='.tmp',
            prefix=path.stem + '_'
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Atomic rename
            shutil.move(temp_path, path)
            
        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    def _is_valid_module_name(self, name: str) -> bool:
        """Check if name is a valid Python module name."""
        import keyword
        import re
        
        if not name:
            return False
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            return False
        if keyword.iskeyword(name):
            return False
        return True
    
    def _update_fragment_sync_status(self, fragment_id: str, success: bool, 
                                      error: str = None):
        """Update sync status in database."""
        try:
            self.db_facade.code_fragments.update_sync_status(
                fragment_id, success, error
            )
        except Exception as e:
            logger.error(f"Failed to update sync status in DB: {e}")
    
    # ==========================================================================
    # CALLBACKS
    # ==========================================================================
    
    def add_callback(self, callback: Callable[[str, SyncStatus], None]):
        """Add callback to be notified of sync events."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str, SyncStatus], None]):
        """Remove callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _notify_callbacks(self, module_name: str, status: SyncStatus):
        """Notify all callbacks of sync event."""
        for callback in self._callbacks:
            try:
                callback(module_name, status)
            except Exception as e:
                logger.error(f"Error in sync callback: {e}")
    
    # ==========================================================================
    # STATUS & INFO
    # ==========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current sync service status."""
        with self._lock:
            synced_count = sum(
                1 for info in self._synced_fragments.values()
                if info.status == SyncStatus.SYNCED
            )
            error_count = sum(
                1 for info in self._synced_fragments.values()
                if info.status == SyncStatus.ERROR
            )
        
        return {
            'running': self._running,
            'target_path': str(self.target_path),
            'module_path': str(self.module_path),
            'sync_interval_seconds': self.config.sync_interval_seconds,
            'synced_fragments': synced_count,
            'error_fragments': error_count,
            'total_tracked': len(self._synced_fragments),
            'stats': self._stats.copy(),
        }
    
    def get_synced_fragments(self) -> List[Dict]:
        """Get list of synced fragments."""
        with self._lock:
            return [
                {
                    'fragment_id': info.fragment_id,
                    'module_name': info.module_name,
                    'name': info.name,
                    'checksum': info.checksum,
                    'file_path': info.file_path,
                    'status': info.status.value,
                    'synced_at': info.synced_at.isoformat() if info.synced_at else None,
                    'error': info.error,
                }
                for info in self._synced_fragments.values()
            ]
    
    def get_import_example(self, module_name: str) -> str:
        """Get import example for a fragment."""
        return f"from code_fragments.{module_name} import *"
    
    @property
    def is_running(self) -> bool:
        """Check if service is running."""
        return self._running


# ==========================================================================
# CONVENIENCE FUNCTIONS
# ==========================================================================

_default_service: Optional[CodeFragmentSyncService] = None


def get_sync_service() -> Optional[CodeFragmentSyncService]:
    """Get the default sync service instance."""
    return _default_service


def set_sync_service(service: CodeFragmentSyncService):
    """Set the default sync service instance."""
    global _default_service
    _default_service = service


def initialize_sync_service(db_facade, config: Optional[SyncConfig] = None) -> CodeFragmentSyncService:
    """
    Initialize and start the default sync service.
    
    Args:
        db_facade: Database facade
        config: Optional sync configuration
        
    Returns:
        The initialized service
    """
    global _default_service
    
    _default_service = CodeFragmentSyncService(db_facade, config)
    _default_service.start()
    
    return _default_service
