"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


from .base_engine import BaseExecutionEngine
from typing import Dict, Any
import uuid
import asyncio

class BackgroundEngine(BaseExecutionEngine):
    """Background job execution"""
    
    def get_mode_name(self) -> str:
        return "background"
    
    async def execute(self, job_config: Dict, **kwargs) -> Dict[str, Any]:
        """Execute background job"""
        self.create_session_record()
        
        # Create job record
        job_id = str(uuid.uuid4())
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO background_jobs (
                    job_id, session_id, job_type, job_configuration, status
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                job_id, self.session_id, job_config.get("type", "generic"),
                json.dumps(job_config), "queued"
            ))
            conn.commit()
        
        # Start async execution
        asyncio.create_task(self._execute_job(job_id, job_config))
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "session_id": self.session_id
        }
    
    async def _execute_job(self, job_id: str, job_config: Dict):
        """Execute job asynchronously"""
        try:
            # Update status
            self._update_job_status(job_id, "running", 0)
            
            # Execute based on job type
            if job_config["type"] == "llm_generation":
                result = await self._execute_llm_job(job_config, job_id)
            elif job_config["type"] == "data_processing":
                result = await self._execute_processing_job(job_config, job_id)
            else:
                result = "completed"
            
            # Update completion
            self._update_job_status(job_id, "completed", 100, result)
            
        except Exception as e:
            self._update_job_status(job_id, "failed", error=str(e))
    
    def _update_job_status(
        self,
        job_id: str,
        status: str,
        progress: float = None,
        result: Any = None,
        error: str = None
    ):
        """Update job status"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if progress is not None:
                cursor.execute("""
                    UPDATE background_jobs
                    SET status = ?, progress_percentage = ?
                    WHERE job_id = ?
                """, (status, progress, job_id))
            elif result is not None:
                cursor.execute("""
                    UPDATE background_jobs
                    SET status = ?, result_data = ?
                    WHERE job_id = ?
                """, (status, json.dumps(result), job_id))
            elif error:
                cursor.execute("""
                    UPDATE background_jobs
                    SET status = ?, error_message = ?
                    WHERE job_id = ?
                """, (status, error, job_id))
            conn.commit()
    
    async def _execute_llm_job(self, config: Dict, job_id: str) -> Any:
        """Execute LLM generation job"""
        total = len(config.get("prompts", []))
        results = []
        
        for i, prompt in enumerate(config.get("prompts", [])):
            response = await self.llm_facade.chat_completion_async(
                messages=[{"role": "user", "content": prompt}]
            )
            results.append(response["content"])
            self._update_job_status(job_id, "running", (i + 1) / total * 100)
        
        return results
    
    async def _execute_processing_job(self, config: Dict, job_id: str) -> Any:
        """Execute data processing job"""
        # Implementation
        return "processed"
