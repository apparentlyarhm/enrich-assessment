import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Body
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.dependencies import get_db
from src.models.job import JobStatus

router = APIRouter(prefix="/vendor-webhook", tags=["Webhooks"])

JOBS_COLLECTION = "jobs"


@router.post("/{vendor_id}", status_code=status.HTTP_200_OK)
async def vendor_webhook(
    vendor_id: str,
    payload: Dict[str, Any] = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    print(f"Received webhook from {vendor_id} with payload: {payload}")

    # We can optionally validate the vendor_id as well but since we dont store any vendor information in the DB, we will not do that here.

    request_id_str = payload.get("request_id")
    if not request_id_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload must include 'request_id'."
        )
    
    try:
        request_id = uuid.UUID(request_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 'request_id' format."
        )

    # Prepare the update document for MongoDB
    update_doc = {
        "$set": {
            "result": payload.get("data"),
            "status": JobStatus.COMPLETE.value, # Use the enum's value
        }
    }

    # Find the job by _id and update it
    result = await db[JOBS_COLLECTION].update_one(
        {"_id": request_id},
        update_doc
    )

    # Check if a document was actually found and updated
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {request_id} not found."
        )

    print(f"Job {request_id} marked as complete in DB.")
    return {"status": "ok", "message": f"Data received for job {request_id}"}