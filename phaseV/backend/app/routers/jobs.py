"""
Dapr Jobs API callback endpoints.
"""
from fastapi import APIRouter, Request
import logging

from app.services.notification_service import check_due_tasks_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs")


@router.post("/check-due-tasks")
async def check_due_tasks_job_endpoint(request: Request):
    """
    Dapr Jobs API callback endpoint for checking due tasks.
    """
    try:
        # Get job data from request
        job_data = await request.json()
        logger.info(f"Dapr job triggered with data: {job_data}")
        
        # Execute the notification logic
        await check_due_tasks_job()
        
        logger.info("Dapr job completed successfully")
        return {"status": "SUCCESS", "message": "Checked due tasks successfully"}
    except Exception as e:
        logger.error(f"Error in Dapr job: {e}", exc_info=True)
        return {"status": "ERROR", "message": str(e)}