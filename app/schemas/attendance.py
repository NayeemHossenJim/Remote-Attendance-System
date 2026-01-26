from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CheckInRequest(BaseModel):
    latitude: float
    longitude: float

class CheckInResponse(BaseModel):
    status: str  # PRESENT | ABSENT | PENDING
    message: str
    distance_from_home: Optional[float] = None
    check_in_enabled: bool
    can_request_present: bool

class LateCheckInRequest(BaseModel):
    latitude: float
    longitude: float
    reason: str

class LateCheckInResponse(BaseModel):
    message: str
    request_id: int
    status: str

class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    status: str
    latitude: Optional[float]
    longitude: Optional[float]
    distance_from_home: Optional[float]
    is_late_request: bool
    late_request_reason: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ApprovalRequest(BaseModel):
    attendance_id: int
    approve: bool
    comment: Optional[str] = None

class ApprovalResponse(BaseModel):
    message: str
    attendance_id: int
    status: str
