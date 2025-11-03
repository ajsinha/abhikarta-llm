"""
API Key Rotation System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

import os
import json
import time
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class APIKey:
    """Represents an API key with metadata"""
    key: str
    provider: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    rotation_count: int = 0
    is_active: bool = True
    key_id: str = None
    
    def __post_init__(self):
        if self.key_id is None:
            self.key_id = secrets.token_hex(8)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'APIKey':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if key is expired"""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until expiry"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)


class KeyRotationPolicy:
    """Policy for key rotation"""
    
    def __init__(
        self,
        rotation_interval_days: int = 90,
        warning_days_before: int = 7,
        auto_rotate: bool = False,
        keep_old_key_days: int = 7,
        max_key_age_days: int = 365
    ):
        """
        Initialize rotation policy.
        
        Args:
            rotation_interval_days: How often to rotate keys
            warning_days_before: When to start sending warnings
            auto_rotate: Whether to automatically rotate
            keep_old_key_days: How long to keep old keys active
            max_key_age_days: Maximum age before forced rotation
        """
        self.rotation_interval_days = rotation_interval_days
        self.warning_days_before = warning_days_before
        self.auto_rotate = auto_rotate
        self.keep_old_key_days = keep_old_key_days
        self.max_key_age_days = max_key_age_days
    
    def should_rotate(self, key: APIKey) -> bool:
        """Check if key should be rotated"""
        age_days = (datetime.now() - key.created_at).days
        return age_days >= self.rotation_interval_days
    
    def should_warn(self, key: APIKey) -> bool:
        """Check if warning should be sent"""
        days_until = key.days_until_expiry()
        if days_until is None:
            age_days = (datetime.now() - key.created_at).days
            days_until_rotation = self.rotation_interval_days - age_days
            return days_until_rotation <= self.warning_days_before
        return days_until <= self.warning_days_before
    
    def must_rotate(self, key: APIKey) -> bool:
        """Check if key must be rotated (exceeded max age)"""
        age_days = (datetime.now() - key.created_at).days
        return age_days >= self.max_key_age_days


class KeyRotationManager:
    """
    Manages API key rotation with zero-downtime strategy.
    
    Features:
    - Automatic key rotation
    - Gradual rollover (old + new keys work during transition)
    - Notification system
    - Multiple provider support
    - Persistent storage
    """
    
    def __init__(
        self,
        storage_path: str = ".keys",
        policy: Optional[KeyRotationPolicy] = None,
        notification_callback: Optional[Callable] = None
    ):
        """
        Initialize key rotation manager.
        
        Args:
            storage_path: Path to store key metadata
            policy: Rotation policy (uses default if None)
            notification_callback: Function to call for notifications
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True, parents=True)
        
        self.policy = policy or KeyRotationPolicy()
        self.notification_callback = notification_callback
        
        self.keys: Dict[str, List[APIKey]] = {}  # provider -> list of keys
        self.load_keys()
        
        # Start background checker if auto-rotate enabled
        self._stop_checker = False
        if self.policy.auto_rotate:
            self._start_checker_thread()
    
    def register_provider(
        self,
        provider: str,
        api_key: str,
        rotation_generator: Optional[Callable[[], str]] = None
    ):
        """
        Register a provider for key rotation.
        
        Args:
            provider: Provider name (e.g., 'anthropic', 'openai')
            api_key: Current API key
            rotation_generator: Function to generate new keys
        """
        key_obj = APIKey(
            key=api_key,
            provider=provider,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.policy.rotation_interval_days)
        )
        
        if provider not in self.keys:
            self.keys[provider] = []
        
        # Deactivate old keys
        for old_key in self.keys[provider]:
            old_key.is_active = False
        
        self.keys[provider].append(key_obj)
        self.save_keys()
        
        logger.info(f"Registered API key for provider: {provider}")
    
    def get_active_key(self, provider: str) -> Optional[str]:
        """
        Get the active API key for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Active API key or None
        """
        if provider not in self.keys:
            return None
        
        active_keys = [k for k in self.keys[provider] if k.is_active and not k.is_expired()]
        
        if not active_keys:
            return None
        
        # Return most recent active key
        key = max(active_keys, key=lambda k: k.created_at)
        key.last_used = datetime.now()
        self.save_keys()
        
        return key.key
    
    def rotate_key(
        self,
        provider: str,
        new_key: str,
        immediate: bool = False
    ) -> bool:
        """
        Rotate API key for a provider.
        
        Args:
            provider: Provider name
            new_key: New API key
            immediate: If True, deactivate old keys immediately
            
        Returns:
            True if successful
        """
        if provider not in self.keys:
            logger.error(f"Provider not registered: {provider}")
            return False
        
        # Create new key
        new_key_obj = APIKey(
            key=new_key,
            provider=provider,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.policy.rotation_interval_days),
            rotation_count=self.keys[provider][-1].rotation_count + 1 if self.keys[provider] else 0
        )
        
        # Add new key
        self.keys[provider].append(new_key_obj)
        
        # Handle old keys
        if immediate:
            # Deactivate immediately
            for old_key in self.keys[provider][:-1]:
                old_key.is_active = False
        else:
            # Schedule deactivation
            deactivation_date = datetime.now() + timedelta(days=self.policy.keep_old_key_days)
            for old_key in self.keys[provider][:-1]:
                if old_key.expires_at is None or old_key.expires_at > deactivation_date:
                    old_key.expires_at = deactivation_date
        
        self.save_keys()
        
        logger.info(f"Rotated API key for provider: {provider}")
        
        # Send notification
        if self.notification_callback:
            self.notification_callback(
                event='key_rotated',
                provider=provider,
                key_id=new_key_obj.key_id
            )
        
        return True
    
    def check_and_notify(self):
        """Check all keys and send notifications if needed"""
        for provider, keys in self.keys.items():
            active_keys = [k for k in keys if k.is_active]
            
            for key in active_keys:
                # Check if rotation needed
                if self.policy.must_rotate(key):
                    logger.critical(f"URGENT: Key for {provider} has exceeded maximum age!")
                    if self.notification_callback:
                        self.notification_callback(
                            event='key_expired',
                            provider=provider,
                            key_id=key.key_id
                        )
                
                elif self.policy.should_rotate(key):
                    if self.policy.auto_rotate:
                        logger.info(f"Auto-rotating key for {provider}")
                        # In practice, you'd call the provider's API to generate a new key
                        # For now, we just log it
                        if self.notification_callback:
                            self.notification_callback(
                                event='auto_rotation_needed',
                                provider=provider,
                                key_id=key.key_id
                            )
                    else:
                        logger.warning(f"Key for {provider} should be rotated")
                        if self.notification_callback:
                            self.notification_callback(
                                event='rotation_recommended',
                                provider=provider,
                                key_id=key.key_id
                            )
                
                elif self.policy.should_warn(key):
                    days_left = key.days_until_expiry()
                    logger.info(f"Key for {provider} will expire in {days_left} days")
                    if self.notification_callback:
                        self.notification_callback(
                            event='expiry_warning',
                            provider=provider,
                            key_id=key.key_id,
                            days_remaining=days_left
                        )
    
    def get_status(self) -> Dict:
        """Get status of all keys"""
        status = {}
        
        for provider, keys in self.keys.items():
            active_keys = [k for k in keys if k.is_active and not k.is_expired()]
            
            if active_keys:
                latest_key = max(active_keys, key=lambda k: k.created_at)
                age_days = (datetime.now() - latest_key.created_at).days
                
                status[provider] = {
                    'active': True,
                    'key_id': latest_key.key_id,
                    'age_days': age_days,
                    'days_until_expiry': latest_key.days_until_expiry(),
                    'should_rotate': self.policy.should_rotate(latest_key),
                    'must_rotate': self.policy.must_rotate(latest_key),
                    'rotation_count': latest_key.rotation_count
                }
            else:
                status[provider] = {
                    'active': False,
                    'message': 'No active keys'
                }
        
        return status
    
    def save_keys(self):
        """Save keys to storage"""
        data = {}
        for provider, keys in self.keys.items():
            data[provider] = [k.to_dict() for k in keys]
        
        file_path = self.storage_path / "keys.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_keys(self):
        """Load keys from storage"""
        file_path = self.storage_path / "keys.json"
        
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            for provider, keys_data in data.items():
                self.keys[provider] = [APIKey.from_dict(k) for k in keys_data]
        except Exception as e:
            logger.error(f"Failed to load keys: {e}")
    
    def _start_checker_thread(self):
        """Start background thread to check keys periodically"""
        def checker():
            while not self._stop_checker:
                self.check_and_notify()
                time.sleep(3600)  # Check every hour
        
        thread = threading.Thread(target=checker, daemon=True)
        thread.start()
    
    def cleanup_old_keys(self, days_old: int = 90):
        """Remove old inactive keys from storage"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for provider in self.keys:
            self.keys[provider] = [
                k for k in self.keys[provider]
                if k.is_active or k.created_at >= cutoff_date
            ]
        
        self.save_keys()
        logger.info(f"Cleaned up keys older than {days_old} days")
    
    def __del__(self):
        """Cleanup on deletion"""
        self._stop_checker = True


# Notification helpers
def email_notification(
    event: str,
    provider: str,
    key_id: str,
    email_to: str,
    **kwargs
):
    """Send email notification (implement with your email service)"""
    logger.info(f"Email notification: {event} for {provider} (key: {key_id})")
    # Implement actual email sending here


def slack_notification(
    event: str,
    provider: str,
    key_id: str,
    webhook_url: str,
    **kwargs
):
    """Send Slack notification (implement with Slack webhook)"""
    logger.info(f"Slack notification: {event} for {provider} (key: {key_id})")
    # Implement actual Slack webhook here


def pagerduty_notification(
    event: str,
    provider: str,
    key_id: str,
    service_key: str,
    **kwargs
):
    """Send PagerDuty alert"""
    logger.critical(f"PagerDuty alert: {event} for {provider} (key: {key_id})")
    # Implement actual PagerDuty integration here
