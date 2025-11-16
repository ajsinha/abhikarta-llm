"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import json
import asyncio

class ListeningEngine(BaseExecutionEngine):
    """Kafka event-driven execution"""
    
    def get_mode_name(self) -> str:
        return "listening"
    
    async def execute(self, subscription_id: str, **kwargs) -> Dict[str, Any]:
        """Start listening to Kafka events"""
        self.create_session_record()
        self.update_session_status("running")
        
        try:
            # Load subscription
            subscription = self._load_subscription(subscription_id)
            
            # Start listening (in background)
            asyncio.create_task(self._listen_loop(subscription))
            
            return {
                "success": True,
                "status": "listening",
                "subscription_id": subscription_id,
                "session_id": self.session_id
            }
        except Exception as e:
            self.update_session_status("failed", str(e))
            return {"success": False, "error": str(e)}
    
    def _load_subscription(self, subscription_id: str) -> Dict:
        """Load subscription configuration"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM event_subscriptions
                WHERE subscription_id = ?
            """, (subscription_id,))
            return dict(cursor.fetchone())
    
    async def _listen_loop(self, subscription: Dict):
        """Main listening loop"""
        kafka_config = json.loads(subscription["kafka_config"])
        
        # Simplified Kafka consumer simulation
        while True:
            event = await self._poll_event(kafka_config)
            if event:
                await self._handle_event(subscription, event)
            await asyncio.sleep(1)
    
    async def _poll_event(self, kafka_config: Dict) -> Dict:
        """Poll for Kafka event"""
        # Mock implementation - replace with actual Kafka consumer
        return None
    
    async def _handle_event(self, subscription: Dict, event: Dict):
        """Handle incoming event"""
        log_id = str(uuid.uuid4())
        handler_type = subscription["handler_type"]
        
        # Log event
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO event_processing_log (
                    log_id, subscription_id, event_data, status
                ) VALUES (?, ?, ?, ?)
            """, (log_id, subscription["subscription_id"], json.dumps(event), "processing"))
            conn.commit()
        
        try:
            # Execute handler
            if handler_type == "planner":
                from .planning_engine import PlanningEngine
                engine = PlanningEngine(
                    user_id=event.get("user_id"),
                    llm_facade=self.llm_facade,
                    tool_registry=self.tool_registry,
                    db_manager=self.db_manager
                )
                result = await engine.execute(goal=event.get("goal", ""))
            
            # Update log
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE event_processing_log
                    SET status = ?, result_data = ?
                    WHERE log_id = ?
                """, ("completed", json.dumps(result), log_id))
                conn.commit()
        
        except Exception as e:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE event_processing_log
                    SET status = ?, error_message = ?
                    WHERE log_id = ?
                """, ("failed", str(e), log_id))
                conn.commit()
