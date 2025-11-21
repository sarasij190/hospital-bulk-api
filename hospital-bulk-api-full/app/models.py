from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class HospitalRowResult(BaseModel):
    row: int
    hospital_id: Optional[int]
    name: str
    status: str
    error: Optional[str] = None

class BulkReport(BaseModel):
    batch_id: UUID
    total_hospitals: int
    processed_hospitals: int
    failed_hospitals: int
    processing_time_seconds: float
    batch_activated: bool
    hospitals: List[HospitalRowResult]
