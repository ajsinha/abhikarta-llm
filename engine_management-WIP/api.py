"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Dict, Any, Optional
from .database.db_manager import DatabaseManager
from .engines import *
from tool_management.registry import ToolRegistry
from integrations.kafka_integration import KafkaConsumerAdapter

class AbhikartaExecutionAPI:
    """Main API for Abhikarta LLM Execution System"""
    
    def __init__(
        self,
        db_path: str = "llm_execution.db",
        llm_facade = None,
        tool_registry = None,
        vector_store = None
    ):
        """
        Initialize the execution API
        
        Args:
            db_path: Path to SQLite database
            llm_facade: LLM facade instance
            tool_registry: Tool registry instance
            vector_store: Vector store instance
        """
        self.db_manager = DatabaseManager(db_path)
        self.llm_facade = llm_facade
        self.tool_registry = tool_registry or ToolRegistry()
        self.vector_store = vector_store
        
        # Initialize database
        self.db_manager.initialize_schema()
    
    async def execute_chat(
        self,
        user_id: str,
        message: str,
        session_id: str = None,
        config: Dict = None
    ) -> Dict[str, Any]:
        """Execute chat mode"""
        from .engines.chat_engine import ChatEngine
        
        engine = ChatEngine(
            session_id=session_id,
            user_id=user_id,
            llm_facade=self.llm_facade,
            tool_registry=self.tool_registry,
            vector_store=self.vector_store,
            db_manager=self.db_manager,
            config=config or {}
        )
        
        return await engine.execute(user_message=message)
    
    async def execute_react(
        self,
        user_id: str,
        goal: str,
        session_id: str = None,
        max_iterations: int = 10,
        config: Dict = None
    ) -> Dict[str, Any]:
        """Execute ReAct mode"""
        from .engines.react_engine import ReActEngine
        
        engine = ReActEngine(
            session_id=session_id,
            user_id=user_id,
            llm_facade=self.llm_facade,
            tool_registry=self.tool_registry,
            vector_store=self.vector_store,
            db_manager=self.db_manager,
            config=config or {}
        )
        
        return await engine.execute(goal=goal, max_iterations=max_iterations)
    
    async def execute_rag(
        self,
        user_id: str,
        query: str,
        collection_id: str,
        session_id: str = None,
        top_k: int = 5,
        config: Dict = None
    ) -> Dict[str, Any]:
        """Execute RAG mode"""
        from .engines.rag_engine import RAGEngine
        
        engine = RAGEngine(
            session_id=session_id,
            user_id=user_id,
            llm_facade=self.llm_facade,
            tool_registry=self.tool_registry,
            vector_store=self.vector_store,
            db_manager=self.db_manager,
            config=config or {}
        )
        
        return await engine.execute(
            query=query,
            collection_id=collection_id,
            top_k=top_k
        )
    
    async def execute_dag(
        self,
        user_id: str,
        dag_id: str,
        inputs: Dict[str, Any] = None,
        session_id: str = None,
        config: Dict = None
    ) -> Dict[str, Any]:
        """Execute DAG mode"""
        from .engines.dag_engine import DAGEngine
        
        engine = DAGEngine(
            session_id=session_id,
            user_id=user_id,
            llm_facade=self.llm_facade,
            tool_registry=self.tool_registry,
            vector_store=self.vector_store,
            db_manager=self.db_manager,
            config=config or {}
        )
        
        return await engine.execute(dag_id=dag_id, inputs=inputs)
    
    # Add similar methods for all other modes...
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM execution_sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_sessions(
        self,
        user_id: str,
        status: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """List user sessions"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT * FROM execution_sessions
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (user_id, status, limit))
            else:
                cursor.execute("""
                    SELECT * FROM execution_sessions
                    WHERE user_id = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
