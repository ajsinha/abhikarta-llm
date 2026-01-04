"""
Code Fragment Delegate - Database operations for Code Fragments.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.3.0
"""

from typing import Any, Dict, List, Optional
import uuid
import json
import logging

from ..database_delegate import DatabaseDelegate

logger = logging.getLogger(__name__)


class CodeFragmentDelegate(DatabaseDelegate):
    """
    Delegate for code fragment database operations.
    
    Handles table: code_fragments
    """
    
    def get_all_fragments(self, category: str = None, language: str = None,
                          is_active: bool = True) -> List[Dict]:
        """Get all code fragments with optional filters."""
        query = "SELECT * FROM code_fragments"
        conditions = []
        params = []
        
        if is_active:
            conditions.append("is_active = 1")
        if category:
            conditions.append("category = ?")
            params.append(category)
        if language:
            conditions.append("language = ?")
            params.append(language)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY category, name"
        return self.fetch_all(query, tuple(params) if params else None) or []
    
    def get_fragment(self, fragment_id: str) -> Optional[Dict]:
        """Get fragment by ID."""
        return self.fetch_one(
            "SELECT * FROM code_fragments WHERE fragment_id = ?",
            (fragment_id,)
        )
    
    def get_fragment_by_name(self, name: str) -> Optional[Dict]:
        """Get fragment by name."""
        return self.fetch_one(
            "SELECT * FROM code_fragments WHERE name = ?",
            (name,)
        )
    
    def get_fragments_count(self, is_active: bool = True) -> int:
        """Get count of fragments."""
        where = "is_active = 1" if is_active else None
        return self.get_count("code_fragments", where)
    
    def get_user_fragments(self, user_id: str) -> List[Dict]:
        """Get fragments created by a user."""
        return self.fetch_all(
            """SELECT * FROM code_fragments 
               WHERE created_by = ? 
               ORDER BY created_at DESC""",
            (user_id,)
        ) or []
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        results = self.fetch_all(
            """SELECT DISTINCT category FROM code_fragments 
               WHERE is_active = 1 ORDER BY category"""
        ) or []
        return [r['category'] for r in results]
    
    def get_fragments_by_category(self, category: str) -> List[Dict]:
        """Get all fragments in a category."""
        return self.fetch_all(
            """SELECT * FROM code_fragments 
               WHERE category = ? AND is_active = 1
               ORDER BY name""",
            (category,)
        ) or []
    
    def create_fragment(self, name: str, code: str, created_by: str,
                        description: str = None, language: str = 'python',
                        version: str = '1.0.0', category: str = 'general',
                        tags: str = '[]', dependencies: str = '[]',
                        is_active: int = 1, is_system: int = 0,
                        status: str = 'draft', source: str = 'web') -> Optional[str]:
        """Create a new code fragment and return fragment_id."""
        fragment_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO code_fragments 
                   (fragment_id, name, description, language, code, version,
                    category, tags, dependencies, is_active, is_system, 
                    status, source, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (fragment_id, name, description, language, code, version,
                 category, tags, dependencies, is_active, is_system,
                 status, source, created_by)
            )
            return fragment_id
        except Exception as e:
            logger.error(f"Error creating fragment: {e}")
            return None
    
    def update_fragment(self, fragment_id: str, updated_by: str = None,
                        **kwargs) -> bool:
        """Update fragment fields."""
        if not kwargs:
            return False
        
        valid_fields = ['name', 'description', 'language', 'code', 'version',
                        'category', 'tags', 'dependencies', 'is_active', 'status', 'source']
        
        updates = ['updated_by = ?', 'updated_at = CURRENT_TIMESTAMP']
        params = [updated_by]
        
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if len(updates) == 2:  # Only updated_by and updated_at
            return False
        
        params.append(fragment_id)
        query = f"UPDATE code_fragments SET {', '.join(updates)} WHERE fragment_id = ?"
        
        try:
            self.execute(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating fragment: {e}")
            return False
    
    def update_code(self, fragment_id: str, code: str,
                    updated_by: str = None) -> bool:
        """Update fragment code."""
        try:
            self.execute(
                """UPDATE code_fragments 
                   SET code = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE fragment_id = ?""",
                (code, updated_by, fragment_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating code: {e}")
            return False
    
    def increment_usage(self, fragment_id: str) -> bool:
        """Increment fragment usage count."""
        try:
            self.execute(
                """UPDATE code_fragments 
                   SET usage_count = usage_count + 1
                   WHERE fragment_id = ?""",
                (fragment_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error incrementing usage: {e}")
            return False
    
    def activate_fragment(self, fragment_id: str) -> bool:
        """Activate a fragment."""
        try:
            self.execute(
                "UPDATE code_fragments SET is_active = 1 WHERE fragment_id = ?",
                (fragment_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error activating fragment: {e}")
            return False
    
    def deactivate_fragment(self, fragment_id: str) -> bool:
        """Deactivate a fragment."""
        try:
            self.execute(
                "UPDATE code_fragments SET is_active = 0 WHERE fragment_id = ?",
                (fragment_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deactivating fragment: {e}")
            return False
    
    def delete_fragment(self, fragment_id: str) -> bool:
        """Delete a fragment."""
        try:
            self.execute(
                "DELETE FROM code_fragments WHERE fragment_id = ?",
                (fragment_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting fragment: {e}")
            return False
    
    def fragment_exists(self, fragment_id: str) -> bool:
        """Check if fragment exists."""
        return self.exists("code_fragments", "fragment_id = ?", (fragment_id,))
    
    def name_exists(self, name: str, exclude_id: str = None) -> bool:
        """Check if fragment name already exists."""
        if exclude_id:
            result = self.fetch_one(
                """SELECT COUNT(*) as count FROM code_fragments 
                   WHERE name = ? AND fragment_id != ?""",
                (name, exclude_id)
            )
        else:
            result = self.fetch_one(
                "SELECT COUNT(*) as count FROM code_fragments WHERE name = ?",
                (name,)
            )
        return result.get('count', 0) > 0 if result else False
    
    def search_fragments(self, query: str, limit: int = 50) -> List[Dict]:
        """Search fragments by name, description, or tags."""
        search_term = f"%{query}%"
        return self.fetch_all(
            """SELECT * FROM code_fragments 
               WHERE is_active = 1 
               AND (name LIKE ? OR description LIKE ? OR tags LIKE ?)
               ORDER BY usage_count DESC, name
               LIMIT ?""",
            (search_term, search_term, search_term, limit)
        ) or []
    
    def get_popular_fragments(self, limit: int = 10) -> List[Dict]:
        """Get most used fragments."""
        return self.fetch_all(
            """SELECT * FROM code_fragments 
               WHERE is_active = 1
               ORDER BY usage_count DESC
               LIMIT ?""",
            (limit,)
        ) or []
    
    def get_recent_fragments(self, limit: int = 10) -> List[Dict]:
        """Get recently created fragments."""
        return self.fetch_all(
            """SELECT * FROM code_fragments 
               WHERE is_active = 1
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,)
        ) or []
    
    # ==========================================================================
    # STATUS MANAGEMENT METHODS (v1.4.8)
    # ==========================================================================
    
    # Valid status transitions for approval workflow
    STATUS_TRANSITIONS = {
        'draft': ['testing', 'pending_review'],
        'testing': ['draft', 'pending_review'],
        'pending_review': ['testing', 'approved', 'draft'],
        'approved': ['published', 'pending_review'],
        'published': ['approved', 'archived'],
        'archived': ['draft']
    }
    
    def get_fragments_by_status(self, status: str, is_active: bool = None) -> List[Dict]:
        """Get fragments by status."""
        query = "SELECT * FROM code_fragments WHERE status = ?"
        params = [status]
        
        if is_active is not None:
            query += " AND is_active = ?"
            params.append(1 if is_active else 0)
        
        query += " ORDER BY updated_at DESC"
        return self.fetch_all(query, tuple(params)) or []
    
    def get_pending_review_fragments(self) -> List[Dict]:
        """Get fragments pending admin review."""
        return self.get_fragments_by_status('pending_review')
    
    def get_approved_fragments(self) -> List[Dict]:
        """Get approved fragments (usable in workflows, agents, etc.)."""
        return self.fetch_all(
            """SELECT * FROM code_fragments 
               WHERE status IN ('approved', 'published') AND is_active = 1
               ORDER BY category, name"""
        ) or []
    
    def get_published_fragments(self) -> List[Dict]:
        """Get published fragments available to all users."""
        return self.get_fragments_by_status('published', is_active=True)
    
    def get_status_counts(self) -> Dict[str, int]:
        """Get count of fragments by status."""
        results = self.fetch_all(
            """SELECT status, COUNT(*) as count 
               FROM code_fragments 
               GROUP BY status"""
        ) or []
        return {r['status']: r['count'] for r in results}
    
    def update_status(self, fragment_id: str, new_status: str, 
                      reviewed_by: str = None, review_notes: str = None) -> bool:
        """Update fragment status with validation."""
        fragment = self.get_fragment(fragment_id)
        if not fragment:
            logger.error(f"Fragment not found: {fragment_id}")
            return False
        
        current_status = fragment.get('status', 'draft')
        
        # Validate status transition
        if new_status not in self.STATUS_TRANSITIONS.get(current_status, []):
            logger.error(f"Invalid status transition: {current_status} -> {new_status}")
            return False
        
        try:
            self.execute(
                """UPDATE code_fragments 
                   SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP,
                       review_notes = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE fragment_id = ?""",
                (new_status, reviewed_by, review_notes, fragment_id)
            )
            logger.info(f"Fragment {fragment_id} status: {current_status} -> {new_status}")
            return True
        except Exception as e:
            logger.error(f"Error updating fragment status: {e}")
            return False
    
    def submit_for_review(self, fragment_id: str, submitted_by: str) -> bool:
        """Submit fragment for admin review."""
        fragment = self.get_fragment(fragment_id)
        if not fragment:
            return False
        
        current_status = fragment.get('status', 'draft')
        if current_status not in ['draft', 'testing']:
            logger.error(f"Cannot submit fragment with status: {current_status}")
            return False
        
        try:
            self.execute(
                """UPDATE code_fragments 
                   SET status = 'pending_review', updated_by = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE fragment_id = ?""",
                (submitted_by, fragment_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error submitting fragment for review: {e}")
            return False
    
    def approve_fragment(self, fragment_id: str, approved_by: str,
                        review_notes: str = None) -> bool:
        """Approve a fragment (admin only)."""
        return self.update_status(fragment_id, 'approved', approved_by, review_notes)
    
    def reject_fragment(self, fragment_id: str, rejected_by: str,
                       review_notes: str = None) -> bool:
        """Reject a fragment back to draft."""
        fragment = self.get_fragment(fragment_id)
        if not fragment:
            return False
        
        try:
            self.execute(
                """UPDATE code_fragments 
                   SET status = 'draft', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP,
                       review_notes = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE fragment_id = ?""",
                (rejected_by, review_notes, fragment_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error rejecting fragment: {e}")
            return False
    
    def publish_fragment(self, fragment_id: str, published_by: str) -> bool:
        """Publish an approved fragment."""
        return self.update_status(fragment_id, 'published', published_by)
    
    def archive_fragment(self, fragment_id: str, archived_by: str,
                        reason: str = None) -> bool:
        """Archive a published fragment."""
        return self.update_status(fragment_id, 'archived', archived_by, reason)
    
    def get_user_fragment_stats(self, user_id: str) -> Dict[str, int]:
        """Get fragment status counts for a user."""
        results = self.fetch_all(
            """SELECT status, COUNT(*) as count 
               FROM code_fragments 
               WHERE created_by = ?
               GROUP BY status""",
            (user_id,)
        ) or []
        return {r['status']: r['count'] for r in results}
    
    def can_be_used(self, fragment_id: str) -> bool:
        """Check if fragment can be used in workflows/agents/etc."""
        fragment = self.get_fragment(fragment_id)
        if not fragment:
            return False
        return fragment.get('status') in ('approved', 'published') and fragment.get('is_active', 0) == 1
    
    def get_usable_fragments(self, category: str = None, 
                             language: str = None) -> List[Dict]:
        """Get fragments that can be used (approved or published)."""
        query = """SELECT * FROM code_fragments 
                   WHERE status IN ('approved', 'published') 
                   AND is_active = 1"""
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        if language:
            query += " AND language = ?"
            params.append(language)
        
        query += " ORDER BY category, name"
        return self.fetch_all(query, tuple(params) if params else None) or []
