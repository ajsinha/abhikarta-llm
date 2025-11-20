"""
LLM Interaction Logger - Data Access Object for logging user interactions

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha | Email: ajsinha@gmail.com

This module provides database persistence for LLM interactions.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class LLMInteractionLogger:
    """
    Data Access Object for logging LLM interactions to database.

    Supports SQLite, PostgreSQL, and MySQL databases.
    Provides methods for inserting and querying interaction logs.
    """

    def __init__(self, db_connection_pool):
        """
        Initialize the interaction logger.

        Args:
            db_connection_pool: Database connection pool instance
        """
        self.db_pool = db_connection_pool
        self.db_type = self._detect_db_type()

        logger.info(f"LLMInteractionLogger initialized with {self.db_type} database")

    def _detect_db_type(self) -> str:
        """
        Detect the database type from connection pool.

        Returns:
            Database type: 'sqlite', 'postgresql', or 'mysql'
        """
        try:
            # Try to detect from connection pool attributes or connection
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Try SQLite-specific query
                try:
                    cursor.execute("SELECT sqlite_version()")
                    return 'sqlite'
                except:
                    pass

                # Try PostgreSQL-specific query
                try:
                    cursor.execute("SELECT version()")
                    result = cursor.fetchone()[0]
                    if 'PostgreSQL' in result:
                        return 'postgresql'
                except:
                    pass

                # Try MySQL-specific query
                try:
                    cursor.execute("SELECT VERSION()")
                    result = cursor.fetchone()[0]
                    if 'MySQL' in result or 'MariaDB' in result:
                        return 'mysql'
                except:
                    pass

            # Default to SQLite
            return 'sqlite'

        except Exception as e:
            logger.warning(f"Could not detect database type: {e}, defaulting to sqlite")
            return 'sqlite'

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = self.db_pool.get_connection()
        try:
            yield conn
        finally:
            conn.close()

    def log_interaction(self,
                        user_id: str,
                        session_id: str,
                        chat_session_id: str,
                        interaction_type: str,
                        provider_name: str,
                        model_name: str,
                        user_data: str,
                        llm_response: str,
                        request_parameters: Optional[Dict[str, Any]] = None,
                        response_metadata: Optional[Dict[str, Any]] = None,
                        response_time_ms: Optional[int] = None,
                        prompt_tokens: Optional[int] = None,
                        completion_tokens: Optional[int] = None,
                        total_tokens: Optional[int] = None,
                        status: str = 'success',
                        error_message: Optional[str] = None,
                        cached_facade: bool = False,
                        streaming: bool = False,
                        client_ip: Optional[str] = None,
                        user_agent: Optional[str] = None) -> Optional[int]:
        """
        Log an LLM interaction to the database.

        Args:
            user_id: User identifier
            session_id: HTTP session ID
            chat_session_id: Chat session ID (from facade cache)
            interaction_type: Type of interaction (chat, completion, etc.)
            provider_name: LLM provider name
            model_name: Model name
            user_data: User's input/prompt
            llm_response: LLM's response
            request_parameters: Request parameters dict (temperature, etc.)
            response_metadata: Response metadata dict (usage, etc.)
            response_time_ms: Response time in milliseconds
            prompt_tokens: Number of tokens in prompt
            completion_tokens: Number of tokens in completion
            total_tokens: Total tokens used
            status: Interaction status (success, error, timeout)
            error_message: Error message if status != success
            cached_facade: Whether cached facade was used
            streaming: Whether streaming was used
            client_ip: Client IP address
            user_agent: User agent string

        Returns:
            Interaction ID if successful, None otherwise
        """
        try:
            # Convert dicts to JSON strings
            request_params_json = json.dumps(request_parameters) if request_parameters else None
            response_meta_json = json.dumps(response_metadata) if response_metadata else None

            # Build SQL based on database type
            if self.db_type == 'postgresql':
                sql = """
                    INSERT INTO llm_interactions (
                        user_id, session_id, chat_session_id, interaction_type,
                        provider_name, model_name, user_data, llm_response,
                        request_parameters, response_metadata,
                        response_time_ms, prompt_tokens, completion_tokens, total_tokens,
                        status, error_message, cached_facade, streaming,
                        client_ip, user_agent
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s::jsonb, %s::jsonb,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING interaction_id
                """
            elif self.db_type == 'mysql':
                sql = """
                    INSERT INTO llm_interactions (
                        user_id, session_id, chat_session_id, interaction_type,
                        provider_name, model_name, user_data, llm_response,
                        request_parameters, response_metadata,
                        response_time_ms, prompt_tokens, completion_tokens, total_tokens,
                        status, error_message, cached_facade, streaming,
                        client_ip, user_agent
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
            else:  # sqlite
                sql = """
                    INSERT INTO llm_interactions (
                        user_id, session_id, chat_session_id, interaction_type,
                        provider_name, model_name, user_data, llm_response,
                        request_parameters, response_metadata,
                        response_time_ms, prompt_tokens, completion_tokens, total_tokens,
                        status, error_message, cached_facade, streaming,
                        client_ip, user_agent
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """

            params = (
                user_id, session_id, chat_session_id, interaction_type,
                provider_name, model_name, user_data, llm_response,
                request_params_json, response_meta_json,
                response_time_ms, prompt_tokens, completion_tokens, total_tokens,
                status, error_message, cached_facade, streaming,
                client_ip, user_agent
            )

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)

                # Get the inserted ID
                if self.db_type == 'postgresql':
                    interaction_id = cursor.fetchone()[0]
                elif self.db_type == 'mysql':
                    interaction_id = cursor.lastrowid
                else:  # sqlite
                    interaction_id = cursor.lastrowid

                conn.commit()

                logger.debug(
                    f"Logged interaction {interaction_id}: "
                    f"user={user_id}, session={chat_session_id}, "
                    f"provider={provider_name}, model={model_name}"
                )

                return interaction_id

        except Exception as e:
            logger.error(f"Error logging interaction: {e}", exc_info=True)
            return None

    def get_user_interactions(self,
                              user_id: str,
                              limit: int = 50,
                              offset: int = 0,
                              session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get interactions for a specific user.

        Args:
            user_id: User identifier
            limit: Maximum number of results
            offset: Offset for pagination
            session_id: Optional chat session ID filter

        Returns:
            List of interaction dictionaries
        """
        try:
            if self.db_type in ['postgresql', 'mysql']:
                placeholder = '%s'
            else:
                placeholder = '?'

            if session_id:
                sql = f"""
                    SELECT * FROM llm_interactions
                    WHERE user_id = {placeholder} AND chat_session_id = {placeholder}
                    ORDER BY interaction_timestamp DESC
                    LIMIT {placeholder} OFFSET {placeholder}
                """
                params = (user_id, session_id, limit, offset)
            else:
                sql = f"""
                    SELECT * FROM llm_interactions
                    WHERE user_id = {placeholder}
                    ORDER BY interaction_timestamp DESC
                    LIMIT {placeholder} OFFSET {placeholder}
                """
                params = (user_id, limit, offset)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)

                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    result = dict(zip(columns, row))

                    # Parse JSON fields
                    if result.get('request_parameters'):
                        try:
                            result['request_parameters'] = json.loads(result['request_parameters'])
                        except:
                            pass

                    if result.get('response_metadata'):
                        try:
                            result['response_metadata'] = json.loads(result['response_metadata'])
                        except:
                            pass

                    results.append(result)

                return results

        except Exception as e:
            logger.error(f"Error getting user interactions: {e}", exc_info=True)
            return []

    def get_session_interactions(self, chat_session_id: str) -> List[Dict[str, Any]]:
        """
        Get all interactions for a specific chat session.

        Args:
            chat_session_id: Chat session identifier

        Returns:
            List of interaction dictionaries
        """
        try:
            placeholder = '%s' if self.db_type in ['postgresql', 'mysql'] else '?'

            sql = f"""
                SELECT * FROM llm_interactions
                WHERE chat_session_id = {placeholder}
                ORDER BY interaction_timestamp
            """

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (chat_session_id,))

                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    result = dict(zip(columns, row))

                    # Parse JSON fields
                    if result.get('request_parameters'):
                        try:
                            result['request_parameters'] = json.loads(result['request_parameters'])
                        except:
                            pass

                    if result.get('response_metadata'):
                        try:
                            result['response_metadata'] = json.loads(result['response_metadata'])
                        except:
                            pass

                    results.append(result)

                return results

        except Exception as e:
            logger.error(f"Error getting session interactions: {e}", exc_info=True)
            return []

    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with user statistics
        """
        try:
            placeholder = '%s' if self.db_type in ['postgresql', 'mysql'] else '?'

            sql = f"""
                SELECT 
                    COUNT(*) as total_interactions,
                    COUNT(DISTINCT chat_session_id) as unique_sessions,
                    MIN(interaction_timestamp) as first_interaction,
                    MAX(interaction_timestamp) as last_interaction,
                    SUM(total_tokens) as total_tokens_used,
                    AVG(response_time_ms) as avg_response_time_ms
                FROM llm_interactions
                WHERE user_id = {placeholder}
            """

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id,))

                columns = [desc[0] for desc in cursor.description]
                row = cursor.fetchone()

                if row:
                    return dict(zip(columns, row))

                return {}

        except Exception as e:
            logger.error(f"Error getting user statistics: {e}", exc_info=True)
            return {}

    def get_provider_statistics(self) -> List[Dict[str, Any]]:
        """
        Get statistics by provider and model.

        Returns:
            List of statistics dictionaries
        """
        try:
            sql = """
                SELECT 
                    provider_name,
                    model_name,
                    COUNT(*) as total_interactions,
                    AVG(response_time_ms) as avg_response_time_ms,
                    SUM(total_tokens) as total_tokens_used
                FROM llm_interactions
                GROUP BY provider_name, model_name
                ORDER BY total_interactions DESC
            """

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)

                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results

        except Exception as e:
            logger.error(f"Error getting provider statistics: {e}", exc_info=True)
            return []

    def delete_old_interactions(self, days_old: int = 90) -> int:
        """
        Delete interactions older than specified days.

        Args:
            days_old: Delete interactions older than this many days

        Returns:
            Number of rows deleted
        """
        try:
            if self.db_type == 'postgresql':
                sql = """
                    DELETE FROM llm_interactions
                    WHERE interaction_timestamp < CURRENT_TIMESTAMP - INTERVAL '%s days'
                """
                params = (days_old,)
            elif self.db_type == 'mysql':
                sql = """
                    DELETE FROM llm_interactions
                    WHERE interaction_timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
                """
                params = (days_old,)
            else:  # sqlite
                sql = """
                    DELETE FROM llm_interactions
                    WHERE interaction_timestamp < datetime('now', '-%s days')
                """
                params = (days_old,)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                deleted_count = cursor.rowcount
                conn.commit()

                logger.info(f"Deleted {deleted_count} interactions older than {days_old} days")
                return deleted_count

        except Exception as e:
            logger.error(f"Error deleting old interactions: {e}", exc_info=True)
            return 0


def create_interaction_logger(db_connection_pool) -> LLMInteractionLogger:
    """
    Factory function to create an LLMInteractionLogger instance.

    Args:
        db_connection_pool: Database connection pool

    Returns:
        Configured LLMInteractionLogger instance
    """
    return LLMInteractionLogger(db_connection_pool)


__all__ = ['LLMInteractionLogger', 'create_interaction_logger']