"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

class GraphState(TypedDict):
    """Base graph state"""
    messages: Annotated[list, operator.add]
    session_id: str
    user_id: str
    current_step: str
    data: Dict[str, Any]

class LangGraphAdapter:
    """Adapter for LangGraph integration"""
    
    def __init__(self, llm_facade, tool_registry, db_manager):
        self.llm_facade = llm_facade
        self.tool_registry = tool_registry
        self.db_manager = db_manager
    
    def create_graph(self, nodes: Dict, edges: Dict, entry_point: str):
        """Create LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        for node_name, node_func in nodes.items():
            workflow.add_node(node_name, node_func)
        
        # Add edges
        for source, targets in edges.items():
            if isinstance(targets, list):
                for target in targets:
                    workflow.add_edge(source, target)
            else:
                workflow.add_edge(source, targets)
        
        # Set entry point
        workflow.set_entry_point(entry_point)
        
        return workflow.compile()
    
    def save_graph_state(self, session_id: str, state: GraphState):
        """Save graph state to database"""
        from ..state_management.state_manager import StateManager
        
        state_mgr = StateManager(self.db_manager)
        state_mgr.save_state(
            session_id,
            state,
            state_type="langgraph",
            node_name=state.get("current_step")
        )
    
    def load_graph_state(self, session_id: str) -> GraphState:
        """Load graph state from database"""
        from ..state_management.state_manager import StateManager
        
        state_mgr = StateManager(self.db_manager)
        return state_mgr.load_state(session_id, state_type="langgraph")
