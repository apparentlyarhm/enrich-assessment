import uuid
import aio_pika
import logging
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from src.core.config import settings
from src.core.dependencies import get_db, get_rabbitmq_channel
from src.models.job import Job, JobCreationResponse, JobStatus, JobStatusResponse, JobCreationRequest

router = APIRouter(prefix="/jobs", tags=["Jobs"])

logger = logging.getLogger(__name__)

@router.post("", response_model=JobCreationResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    job_request: JobCreationRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    channel: aio_pika.Channel = Depends(get_rabbitmq_channel)
):
    """
    Accepts a job request.
    - Accepts any JSON payload.
    - Creates a new job with a unique ID and "pending" status.
    - Responds instantly with the request_id.
    """
    new_job = Job(
        vendor=job_request.vendor,
        vendor_type=job_request.vendor_type,
        payload=job_request.payload
    )
    job_to_insert = new_job.model_dump(by_alias=True)

    # Insert the new job into the collection
    await db[settings.MONGO_COLLECTION_NAME].insert_one(job_to_insert)

    message_body = new_job.model_dump_json(by_alias=True)
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=message_body.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key=settings.RABBITMQ_QUEUE_NAME
    )
    
    logger.info(f"Job created in DB and enqueued: {new_job.request_id}")
    return JobCreationResponse(request_id=new_job.request_id)


@router.get("", response_model=Union[JobStatusResponse, List[Job]])
async def get_job_status(
    request_id: Optional[uuid.UUID] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Looks up a job by its request_id.
    - If request_id is not provided, returns a list of all jobs.
    - If the job is complete, it returns the status and the result.
    - If the job is not complete (pending, processing, etc.), it returns a "processing" status.
    - If the job is not found, it returns a 404 error.
    """
    collection = db[settings.MONGO_COLLECTION_NAME]

    if request_id:
        job_data = await collection.find_one({"_id": request_id})
        if not job_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found."
            )
        job = Job(**job_data)
        if job.status == JobStatus.COMPLETE:
            return JobStatusResponse(status="complete", result=job.result)
        else:
            return JobStatusResponse(status="processing")
    else:
        jobs_cursor = collection.find({})
        jobs_list = []

        async for job_data in jobs_cursor:
            jobs_list.append(Job(**job_data))

        return jobs_list

@router.delete("", status_code=status.HTTP_200_OK)
def delete(
    db: AsyncIOMotorDatabase = Depends(get_db)
): 
    """
    Deletes all jobs in the db. Just a testing endpoint
    """
    db[settings.MONGO_COLLECTION_NAME].delete_many({})
    return None