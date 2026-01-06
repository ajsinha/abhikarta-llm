"""
AI Org Manager - Core orchestration for AI Organizations.

This module manages:
- Organization lifecycle (create, activate, pause, archive)
- Node management (add, remove, restructure)
- Org tree building and validation
- Actor lifecycle for nodes

Version: 1.4.7
Copyright © 2025-2030, All Rights Reserved
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from .models import (
    AIOrg, AINode, AITask, AIResponse, AIEventLog,
    OrgStatus, NodeType, TaskStatus, TaskPriority,
    HumanMirror, HITLConfig
)
from .db_ops import AIORGDBOps

logger = logging.getLogger(__name__)


class OrgManager:
    """
    Manages AI Organization lifecycle and structure.
    
    Responsibilities:
    - Create, load, activate, pause organizations
    - Manage node hierarchy
    - Validate org structure (DAG, single root)
    - Coordinate with actor system
    - Export/import org charts
    """
    
    def __init__(self, db_ops: AIORGDBOps, event_bus=None, actor_system=None):
        """
        Initialize OrgManager.
        
        Args:
            db_ops: Database operations instance
            event_bus: Optional event bus for real-time updates
            actor_system: Optional actor system for node actors
        """
        self.db = db_ops
        self.event_bus = event_bus
        self.actor_system = actor_system
        
        # Cache of active orgs
        self.active_orgs: Dict[str, AIOrg] = {}
        
        # Map of org_id -> {node_id: actor}
        self.node_actors: Dict[str, Dict[str, Any]] = {}
    
    # =========================================================================
    # ORGANIZATION LIFECYCLE
    # =========================================================================
    
    def create_org(
        self,
        name: str,
        description: str,
        created_by: str,
        config: Optional[Dict[str, Any]] = None
    ) -> AIOrg:
        """
        Create a new AI Organization.
        
        Args:
            name: Organization name
            description: Description
            created_by: User ID of creator
            config: Optional configuration
            
        Returns:
            Created AIOrg instance
        """
        org = AIOrg.create(
            name=name,
            description=description,
            created_by=created_by,
            config=config
        )
        
        if self.db.save_org(org):
            logger.info(f"Created AI Org: {org.name} ({org.org_id})")
            
            # Log event
            self._log_event(org.org_id, "ORG_CREATED", {
                "name": name,
                "created_by": created_by
            })
            
            return org
        else:
            raise Exception(f"Failed to save org: {name}")
    
    def load_org(self, org_id: str, include_nodes: bool = True) -> Optional[AIOrg]:
        """
        Load an organization from database.
        
        Args:
            org_id: Organization ID
            include_nodes: Whether to load nodes
            
        Returns:
            AIOrg instance or None
        """
        org = self.db.get_org(org_id)
        if not org:
            return None
        
        if include_nodes:
            nodes = self.db.get_org_nodes(org_id)
            org.nodes = nodes
            
            # Build tree structure
            self._build_node_tree(org)
            
            # Find root
            root = self.db.get_root_node(org_id)
            if root:
                org.root_node_id = root.node_id
        
        return org
    
    def activate_org(self, org_id: str) -> Tuple[bool, str]:
        """
        Activate an organization.
        
        This validates the structure and starts node actors.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Tuple of (success, message)
        """
        org = self.load_org(org_id)
        if not org:
            return False, "Organization not found"
        
        # Validate structure
        valid, message = self._validate_org_structure(org)
        if not valid:
            return False, message
        
        # Update status
        org.status = OrgStatus.ACTIVE
        org.updated_at = datetime.now(timezone.utc)
        
        if not self.db.save_org(org):
            return False, "Failed to update org status"
        
        # Cache active org
        self.active_orgs[org_id] = org
        
        # Start node actors if actor system available
        if self.actor_system:
            self._start_node_actors(org)
        
        # Publish activation event
        if self.event_bus:
            self.event_bus.publish(org.event_bus_channel, {
                "type": "ORG_ACTIVATED",
                "org_id": org_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        self._log_event(org_id, "ORG_ACTIVATED", {})
        
        logger.info(f"Activated AI Org: {org.name}")
        return True, "Organization activated successfully"
    
    def pause_org(self, org_id: str) -> Tuple[bool, str]:
        """
        Pause an organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Tuple of (success, message)
        """
        org = self.db.get_org(org_id)
        if not org:
            return False, "Organization not found"
        
        org.status = OrgStatus.PAUSED
        org.updated_at = datetime.now(timezone.utc)
        
        if not self.db.save_org(org):
            return False, "Failed to update org status"
        
        # Stop node actors
        if org_id in self.node_actors:
            self._stop_node_actors(org_id)
        
        # Remove from active cache
        if org_id in self.active_orgs:
            del self.active_orgs[org_id]
        
        self._log_event(org_id, "ORG_PAUSED", {})
        
        logger.info(f"Paused AI Org: {org.name}")
        return True, "Organization paused successfully"
    
    def archive_org(self, org_id: str) -> Tuple[bool, str]:
        """Archive an organization."""
        org = self.db.get_org(org_id)
        if not org:
            return False, "Organization not found"
        
        # Pause first if active
        if org.status == OrgStatus.ACTIVE:
            self.pause_org(org_id)
        
        org.status = OrgStatus.ARCHIVED
        org.updated_at = datetime.now(timezone.utc)
        
        if not self.db.save_org(org):
            return False, "Failed to archive org"
        
        self._log_event(org_id, "ORG_ARCHIVED", {})
        
        return True, "Organization archived successfully"
    
    def delete_org(self, org_id: str) -> Tuple[bool, str]:
        """
        Delete an organization and all its data.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Tuple of (success, message)
        """
        # Pause first
        self.pause_org(org_id)
        
        if self.db.delete_org(org_id):
            logger.info(f"Deleted AI Org: {org_id}")
            return True, "Organization deleted successfully"
        
        return False, "Failed to delete organization"
    
    # =========================================================================
    # NODE MANAGEMENT
    # =========================================================================
    
    def add_node(
        self,
        org_id: str,
        role_name: str,
        role_type: NodeType,
        description: str = "",
        parent_node_id: Optional[str] = None,
        agent_config: Optional[Dict[str, Any]] = None,
        human_mirror: Optional[HumanMirror] = None,
        hitl_config: Optional[HITLConfig] = None,
        notification_channels: Optional[List[str]] = None,
        position_x: int = 0,
        position_y: int = 0
    ) -> AINode:
        """
        Add a node to the organization.
        
        Args:
            org_id: Organization ID
            role_name: Name of the role
            role_type: Type of node
            description: Role description
            parent_node_id: Parent node (None for root)
            agent_config: AI agent configuration
            human_mirror: Human this node represents
            hitl_config: HITL settings
            notification_channels: Notification preferences
            position_x: X position in visual designer
            position_y: Y position in visual designer
            
        Returns:
            Created AINode instance
        """
        # Validate parent exists if specified
        if parent_node_id:
            parent = self.db.get_node(parent_node_id)
            if not parent:
                raise ValueError(f"Parent node not found: {parent_node_id}")
        else:
            # Check if root already exists
            existing_root = self.db.get_root_node(org_id)
            if existing_root:
                raise ValueError("Organization already has a root node (CEO)")
        
        node = AINode.create(
            org_id=org_id,
            role_name=role_name,
            role_type=role_type,
            description=description,
            parent_node_id=parent_node_id,
            agent_config=agent_config,
            human_mirror=human_mirror,
            hitl_config=hitl_config,
            notification_channels=notification_channels,
            position_x=position_x,
            position_y=position_y
        )
        
        if self.db.save_node(node):
            logger.info(f"Added node: {role_name} to org {org_id}")
            
            self._log_event(org_id, "NODE_ADDED", {
                "node_id": node.node_id,
                "role_name": role_name,
                "parent_node_id": parent_node_id
            })
            
            return node
        else:
            raise Exception(f"Failed to save node: {role_name}")
    
    def update_node(self, node: AINode) -> bool:
        """Update a node's configuration."""
        node.updated_at = datetime.now(timezone.utc)
        return self.db.save_node(node)
    
    def remove_node(self, node_id: str, reassign_children_to: Optional[str] = None) -> Tuple[bool, str]:
        """
        Remove a node from the organization.
        
        Args:
            node_id: Node to remove
            reassign_children_to: Optional parent for children
            
        Returns:
            Tuple of (success, message)
        """
        node = self.db.get_node(node_id)
        if not node:
            return False, "Node not found"
        
        # Check for active tasks
        active_tasks = self.db.get_node_tasks(node_id, TaskStatus.IN_PROGRESS)
        if active_tasks:
            return False, "Node has active tasks"
        
        # Handle children
        children = self.db.get_child_nodes(node_id)
        if children:
            if reassign_children_to:
                # Reassign children to new parent
                for child in children:
                    child.parent_node_id = reassign_children_to
                    self.db.save_node(child)
            else:
                return False, "Node has children. Specify reassignment or delete children first."
        
        if self.db.delete_node(node_id):
            self._log_event(node.org_id, "NODE_REMOVED", {
                "node_id": node_id,
                "role_name": node.role_name
            })
            return True, "Node removed successfully"
        
        return False, "Failed to remove node"
    
    def restructure_node(self, node_id: str, new_parent_id: str) -> Tuple[bool, str]:
        """
        Move a node to a new parent.
        
        Args:
            node_id: Node to move
            new_parent_id: New parent node
            
        Returns:
            Tuple of (success, message)
        """
        node = self.db.get_node(node_id)
        if not node:
            return False, "Node not found"
        
        new_parent = self.db.get_node(new_parent_id)
        if not new_parent:
            return False, "New parent not found"
        
        # Prevent circular reference
        if self._would_create_cycle(node_id, new_parent_id):
            return False, "This would create a circular reference"
        
        old_parent = node.parent_node_id
        node.parent_node_id = new_parent_id
        node.updated_at = datetime.now(timezone.utc)
        
        if self.db.save_node(node):
            self._log_event(node.org_id, "NODE_RESTRUCTURED", {
                "node_id": node_id,
                "old_parent": old_parent,
                "new_parent": new_parent_id
            })
            return True, "Node restructured successfully"
        
        return False, "Failed to restructure node"
    
    def get_node_with_children(self, node_id: str) -> Optional[AINode]:
        """Get a node with its children populated."""
        node = self.db.get_node(node_id)
        if node:
            node.children = self.db.get_child_nodes(node_id)
        return node
    
    # =========================================================================
    # EXPORT / IMPORT
    # =========================================================================
    
    def export_to_json(self, org_id: str) -> Dict[str, Any]:
        """
        Export organization to JSON format.
        
        Args:
            org_id: Organization ID
            
        Returns:
            JSON-serializable dictionary
        """
        org = self.load_org(org_id, include_nodes=True)
        if not org:
            raise ValueError(f"Organization not found: {org_id}")
        
        # Build export structure
        export = {
            "version": "1.4.7",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "org": {
                "name": org.name,
                "description": org.description,
                "config": org.config
            },
            "nodes": []
        }
        
        # Export nodes preserving hierarchy
        for node in org.nodes:
            export["nodes"].append({
                "node_id": node.node_id,
                "parent_node_id": node.parent_node_id,
                "role_name": node.role_name,
                "role_type": node.role_type.value,
                "description": node.description,
                "agent_config": node.agent_config,
                "human_mirror": node.human_mirror.to_dict(),
                "hitl_config": node.hitl_config.to_dict(),
                "notification_channels": node.notification_channels,
                "position_x": node.position_x,
                "position_y": node.position_y
            })
        
        return export
    
    def import_from_json(
        self,
        json_data: Dict[str, Any],
        created_by: str,
        new_name: Optional[str] = None
    ) -> AIOrg:
        """
        Import organization from JSON.
        
        Args:
            json_data: Exported JSON data
            created_by: User importing
            new_name: Optional new name for imported org
            
        Returns:
            Created AIOrg instance
        """
        org_data = json_data.get("org", {})
        nodes_data = json_data.get("nodes", [])
        
        # Create org
        org = self.create_org(
            name=new_name or org_data.get("name", "Imported Org"),
            description=org_data.get("description", ""),
            created_by=created_by,
            config=org_data.get("config", {})
        )
        
        # Map old node IDs to new ones
        id_map = {}
        
        # First pass: create all nodes without parent references
        pending_nodes = []
        for node_data in nodes_data:
            pending_nodes.append(node_data)
        
        # Sort to process root first (no parent), then children
        def sort_key(n):
            return 0 if n.get("parent_node_id") is None else 1
        
        pending_nodes.sort(key=sort_key)
        
        # Create nodes
        for node_data in pending_nodes:
            old_id = node_data.get("node_id")
            old_parent = node_data.get("parent_node_id")
            
            # Map parent ID
            new_parent = id_map.get(old_parent) if old_parent else None
            
            human_data = node_data.get("human_mirror", {})
            hitl_data = node_data.get("hitl_config", {})
            
            node = self.add_node(
                org_id=org.org_id,
                role_name=node_data.get("role_name", "Unnamed"),
                role_type=NodeType(node_data.get("role_type", "analyst")),
                description=node_data.get("description", ""),
                parent_node_id=new_parent,
                agent_config=node_data.get("agent_config", {}),
                human_mirror=HumanMirror.from_dict(human_data),
                hitl_config=HITLConfig.from_dict(hitl_data),
                notification_channels=node_data.get("notification_channels", ["email"]),
                position_x=node_data.get("position_x", 0),
                position_y=node_data.get("position_y", 0)
            )
            
            id_map[old_id] = node.node_id
        
        logger.info(f"Imported org {org.name} with {len(id_map)} nodes")
        return org
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def _validate_org_structure(self, org: AIOrg) -> Tuple[bool, str]:
        """
        Validate organization structure.
        
        Checks:
        - Has exactly one root node
        - No circular references
        - All parent references valid
        """
        if not org.nodes:
            return False, "Organization has no nodes"
        
        # Count root nodes
        root_nodes = [n for n in org.nodes if n.parent_node_id is None]
        if len(root_nodes) == 0:
            return False, "Organization has no root node (CEO)"
        if len(root_nodes) > 1:
            return False, f"Organization has multiple root nodes: {[n.role_name for n in root_nodes]}"
        
        # Check for valid parent references
        node_ids = {n.node_id for n in org.nodes}
        for node in org.nodes:
            if node.parent_node_id and node.parent_node_id not in node_ids:
                return False, f"Node {node.role_name} references non-existent parent"
        
        # Check for cycles
        if self._has_cycle(org.nodes):
            return False, "Organization structure contains circular references"
        
        return True, "Structure is valid"
    
    def _has_cycle(self, nodes: List[AINode]) -> bool:
        """Check if node list contains cycles."""
        node_map = {n.node_id: n for n in nodes}
        visited = set()
        
        def visit(node_id: str, path: set) -> bool:
            if node_id in path:
                return True  # Cycle found
            if node_id in visited:
                return False
            
            visited.add(node_id)
            path.add(node_id)
            
            node = node_map.get(node_id)
            if node and node.parent_node_id:
                if visit(node.parent_node_id, path):
                    return True
            
            path.remove(node_id)
            return False
        
        for node in nodes:
            if visit(node.node_id, set()):
                return True
        
        return False
    
    def _would_create_cycle(self, node_id: str, new_parent_id: str) -> bool:
        """Check if changing parent would create a cycle."""
        # Walk up from new_parent to check if we reach node_id
        current = new_parent_id
        visited = {node_id}  # Start with the node being moved
        
        while current:
            if current in visited:
                return True
            visited.add(current)
            
            node = self.db.get_node(current)
            if not node:
                break
            current = node.parent_node_id
        
        return False
    
    def _build_node_tree(self, org: AIOrg) -> None:
        """Build parent-child relationships in memory."""
        node_map = {n.node_id: n for n in org.nodes}
        
        # Clear existing children
        for node in org.nodes:
            node.children = []
        
        # Build children lists
        for node in org.nodes:
            if node.parent_node_id and node.parent_node_id in node_map:
                parent = node_map[node.parent_node_id]
                parent.children.append(node)
    
    # =========================================================================
    # ACTOR MANAGEMENT
    # =========================================================================
    
    def _start_node_actors(self, org: AIOrg) -> None:
        """Start actors for all nodes in org."""
        if not self.actor_system:
            return
        
        self.node_actors[org.org_id] = {}
        
        for node in org.nodes:
            # Create actor for node
            # This would integrate with the actor system
            # For now, just log
            logger.debug(f"Would start actor for node: {node.role_name}")
    
    def _stop_node_actors(self, org_id: str) -> None:
        """Stop all actors for an org."""
        if org_id in self.node_actors:
            for node_id, actor in self.node_actors[org_id].items():
                logger.debug(f"Would stop actor for node: {node_id}")
            del self.node_actors[org_id]
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def _log_event(
        self,
        org_id: str,
        event_type: str,
        payload: Dict[str, Any],
        source_node_id: Optional[str] = None,
        target_node_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> None:
        """Log an event to the database."""
        event = AIEventLog.create(
            org_id=org_id,
            event_type=event_type,
            payload=payload,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            task_id=task_id
        )
        self.db.save_event_log(event)
    
    def get_org_tree_json(self, org_id: str) -> Dict[str, Any]:
        """
        Get org structure as nested JSON for visual designer.
        
        Returns hierarchical structure suitable for tree visualization.
        """
        org = self.load_org(org_id, include_nodes=True)
        if not org:
            return {}
        
        def node_to_tree(node: AINode) -> Dict[str, Any]:
            return {
                "id": node.node_id,
                "name": node.role_name,
                "type": node.role_type.value,
                "description": node.description,
                "human_name": node.human_mirror.name,
                "human_email": node.human_mirror.email,
                "hitl_enabled": node.hitl_config.enabled,
                "status": node.status,
                "position": {"x": node.position_x, "y": node.position_y},
                "children": [node_to_tree(child) for child in node.children]
            }
        
        # Find root and build tree
        root = next((n for n in org.nodes if n.parent_node_id is None), None)
        if root:
            return {
                "org_id": org.org_id,
                "name": org.name,
                "status": org.status.value,
                "tree": node_to_tree(root)
            }
        
        return {"org_id": org.org_id, "name": org.name, "tree": None}
    
    def get_statistics(self, org_id: str) -> Dict[str, Any]:
        """Get statistics for an organization."""
        return self.db.get_org_stats(org_id)
