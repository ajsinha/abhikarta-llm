"""
Code Fragment Delegate - Database operations for Code Fragments.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.2.1
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
                        is_active: int = 1, is_system: int = 0) -> Optional[str]:
        """Create a new code fragment and return fragment_id."""
        fragment_id = str(uuid.uuid4())
        try:
            self.execute(
                """INSERT INTO code_fragments 
                   (fragment_id, name, description, language, code, version,
                    category, tags, dependencies, is_active, is_system, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (fragment_id, name, description, language, code, version,
                 category, tags, dependencies, is_active, is_system, created_by)
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
                        'category', 'tags', 'dependencies', 'is_active']
        
        updates = ['updated_by = ?']
        params = [updated_by]
        
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if len(updates) == 1:  # Only updated_by
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
