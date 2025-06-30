import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.dependencies import get_db
from src.models.job import Job, JobCreationResponse, JobStatus, JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobCreationResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(
    payload: Dict[str, Any],
    db: Dict[uuid.UUID, Job] = Depends(get_db)
):
    """
    Accepts a job request.
    - Accepts any JSON payload.
    - Creates a new job with a unique ID and "pending" status.
    - Responds instantly with the request_id.
    """
    new_job = Job(payload=payload)
    db[new_job.request_id] = new_job
    
    print(f"Job created: {new_job.request_id}. Current DB state: {db}")

    return JobCreationResponse(request_id=new_job.request_id)


@router.get("/{request_id}", response_model=JobStatusResponse)
def get_job_status(
    request_id: uuid.UUID,
    db: Dict[uuid.UUID, Job] = Depends(get_db)
):
    """
    Looks up a job by its request_id.
    - If the job is complete, it returns the status and the result.
    - If the job is not complete (pending, processing, etc.), it returns a "processing" status.
    - If the job is not found, it returns a 404 error.
    """
    job = db.get(request_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found."
        )

    if job.status == JobStatus.COMPLETE:
        return JobStatusResponse(status="complete", result=job.result)
    else:

        # For client POV, any non-complete status is considered "processing".
        return JobStatusResponse(status="processing")
