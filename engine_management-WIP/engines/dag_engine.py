"""
Abhikarta LLM Platform - dag_engine.py
Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

Legal Notice:
This module and the associated software architecture are proprietary and confidential.
"""

from .base_engine import BaseExecutionEngine
from typing import Dict, Any, List
import json
import uuid

class DAGEngine(BaseExecutionEngine):
    """Directed Acyclic Graph execution engine"""
    
    def get_mode_name(self) -> str:
        return "dag"
    
    async def execute(self, dag_id: str, inputs: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Execute DAG workflow"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Load DAG definition
            dag_def = self._load_dag_definition(dag_id)
            
            # Create execution record
            execution_id = str(uuid.uuid4())
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO dag_executions (
                        execution_id, session_id, dag_id, status
                    ) VALUES (?, ?, ?, ?)
                """, (execution_id, self.session_id, dag_id, "running"))
                conn.commit()
            
            # Execute DAG
            graph = json.loads(dag_def["graph_definition"])
            entry_point = dag_def["entry_point"]
            
            result = await self._execute_node(
                execution_id, graph, entry_point, inputs or {}
            )
            
            # Update execution
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE dag_executions
                    SET status = ?, final_output = ?
                    WHERE execution_id = ?
                """, ("completed", json.dumps(result), execution_id))
                conn.commit()
            
            self.update_session_status("completed")
            
            return {
                "success": True,
                "result": result,
                "execution_id": execution_id,
                "session_id": self.session_id
            }
            
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session_id
            }
    
    def _load_dag_definition(self, dag_id: str) -> Dict:
        """Load DAG definition from database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM dag_definitions WHERE dag_id = ?
            """, (dag_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    async def _execute_node(
        self,
        execution_id: str,
        graph: Dict,
        node_id: str,
        inputs: Dict
    ) -> Any:
        """Execute a single node in the DAG"""
        node = graph["nodes"][node_id]
        node_type = node["type"]
        
        # Execute based on node type
        if node_type == "llm":
            result = await self._execute_llm_node(node, inputs)
        elif node_type == "tool":
            result = await self._execute_tool_node(node, inputs)
        elif node_type == "condition":
            result = await self._execute_condition_node(node, inputs)
        else:
            result = inputs
        
        # Save node result
        # ... (database update)
        
        # Get next nodes
        next_nodes = node.get("next", [])
        if not next_nodes:
            return result
        
        # Execute next nodes
        for next_node_id in next_nodes:
            result = await self._execute_node(execution_id, graph, next_node_id, result)
        
        return result
    
    async def _execute_llm_node(self, node: Dict, inputs: Dict) -> Dict:
        """Execute LLM node"""
        prompt = node["prompt"].format(**inputs)
        response = await self.llm_facade.chat_completion_async(
            messages=[{"role": "user", "content": prompt}]
        )
        return {"result": response["content"], **inputs}
    
    async def _execute_tool_node(self, node: Dict, inputs: Dict) -> Dict:
        """Execute tool node"""
        tool_name = node["tool"]
        tool_inputs = node.get("inputs", {})
        
        # Format inputs
        formatted_inputs = {
            k: v.format(**inputs) if isinstance(v, str) else v
            for k, v in tool_inputs.items()
        }
        
        result = await self.tool_registry.execute(tool_name, **formatted_inputs)
        return {"result": result.data, **inputs}
    
    async def _execute_condition_node(self, node: Dict, inputs: Dict) -> Dict:
        """Execute conditional node"""
        condition = node["condition"]
        # Simple eval for demo - in production use safe evaluation
        if eval(condition, {}, inputs):
            return inputs
        return {}
