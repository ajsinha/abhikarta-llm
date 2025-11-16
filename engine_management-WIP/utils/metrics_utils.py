"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

class MetricsCollector:
    """Collect and track execution metrics"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def record_metric(
        self,
        session_id: str,
        metric_name: str,
        metric_value: float,
        metric_unit: str = None,
        dimensions: Dict[str, Any] = None
    ):
        """Record a metric"""
        import uuid
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_metrics (
                    metric_id, session_id, metric_name,
                    metric_value, metric_unit, dimensions
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                session_id,
                metric_name,
                metric_value,
                metric_unit,
                json.dumps(dimensions or {})
            ))
            conn.commit()
    
    def get_metrics(
        self,
        metric_name: str = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Dict]:
        """Query metrics"""
        query = "SELECT * FROM execution_metrics WHERE 1=1"
        params = []
        
        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)
        
        if start_time:
            query += " AND recorded_at >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND recorded_at <= ?"
            params.append(end_time.isoformat())
        
        query += " ORDER BY recorded_at DESC"
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_aggregated_metrics(
        self,
        metric_name: str,
        aggregation: str = "avg",  # avg, sum, min, max, count
        group_by: str = None,  # hour, day, week, month
        start_time: datetime = None
    ) -> List[Dict]:
        """Get aggregated metrics"""
        agg_func = aggregation.upper()
        
        query = f"""
            SELECT 
                {agg_func}(metric_value) as value,
                metric_name
        """
        
        params = [metric_name]
        
        if group_by:
            if group_by == "hour":
                query += ", strftime('%Y-%m-%d %H:00:00', recorded_at) as time_bucket"
            elif group_by == "day":
                query += ", DATE(recorded_at) as time_bucket"
            elif group_by == "week":
                query += ", strftime('%Y-W%W', recorded_at) as time_bucket"
            elif group_by == "month":
                query += ", strftime('%Y-%m', recorded_at) as time_bucket"
        
        query += " FROM execution_metrics WHERE metric_name = ?"
        
        if start_time:
            query += " AND recorded_at >= ?"
            params.append(start_time.isoformat())
        
        if group_by:
            query += " GROUP BY time_bucket ORDER BY time_bucket"
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

class PerformanceTracker:
    """Track performance metrics for executions"""
    
    def __init__(self, session_id: str, metrics_collector: MetricsCollector):
        self.session_id = session_id
        self.metrics = metrics_collector
        self.timers = {}
    
    def start_timer(self, name: str):
        """Start a named timer"""
        import time
        self.timers[name] = time.time()
    
    def end_timer(self, name: str, record: bool = True) -> float:
        """End timer and optionally record"""
        import time
        if name not in self.timers:
            return 0
        
        duration_ms = (time.time() - self.timers[name]) * 1000
        del self.timers[name]
        
        if record:
            self.metrics.record_metric(
                self.session_id,
                f"duration_{name}",
                duration_ms,
                "milliseconds"
            )
        
        return duration_ms
    
    def record_token_usage(self, prompt_tokens: int, completion_tokens: int):
        """Record token usage"""
        self.metrics.record_metric(
            self.session_id,
            "tokens_prompt",
            prompt_tokens,
            "tokens"
        )
        
        self.metrics.record_metric(
            self.session_id,
            "tokens_completion",
            completion_tokens,
            "tokens"
        )
        
        self.metrics.record_metric(
            self.session_id,
            "tokens_total",
            prompt_tokens + completion_tokens,
            "tokens"
        )
    
    def record_cost(self, cost: float):
        """Record execution cost"""
        self.metrics.record_metric(
            self.session_id,
            "cost",
            cost,
            "usd"
        )
