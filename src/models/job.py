import uuid
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict

class VendorType(str, Enum):
    SYNC = "sync"
    ASYNC = "async"

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(BaseModel):
    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="_id")
    status: JobStatus = JobStatus.PENDING

    # Assuming vendor is a string identifier for the vendor
    vendor: str
    vendor_type: VendorType

    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        populate_by_name=True, # Allows using the alias for population
        arbitrary_types_allowed=True # Needed for ObjectId, though we use UUID here
    )

class JobCreationResponse(BaseModel):
    request_id: uuid.UUID

class JobCreationRequest(BaseModel):
    vendor: str
    vendor_type: VendorType
    request_id: uuid.UUID
    
class JobStatusResponse(BaseModel):
    status: str # e.g., "complete" or "processing"
    result: Optional[Dict[str, Any]] = None
