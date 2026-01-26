from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.attendance import (
    CheckInRequest,
    CheckInResponse,
    LateCheckInRequest,
    LateCheckInResponse,
    AttendanceResponse,
    ApprovalRequest,
    ApprovalResponse
)
from app.services.attendance_service import (
    check_in,
    submit_late_check_in_request,
    approve_late_check_in,
    get_user_attendance_history,
    get_pending_approvals
)
from app.db.session import get_db
from app.api.dependencies import get_current_user, get_current_team_lead
from app.models.user import User

router = APIRouter()

@router.post("/check-in", response_model=CheckInResponse)
def checkin(
    payload: CheckInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check-in endpoint following the flowchart:
    - 08:00-09:30: Check GPS location, mark PRESENT/ABSENT
    - After 09:30: Mark ABSENT, enable late request option
    """
    try:
        result = check_in(db, current_user, payload.latitude, payload.longitude)
        return CheckInResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Check-in failed: {str(e)}"
        )

@router.post("/late-check-in-request", response_model=LateCheckInResponse)
def late_check_in_request(
    payload: LateCheckInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit late check-in request (after 09:30)"""
    try:
        result = submit_late_check_in_request(
            db, current_user, payload.latitude, payload.longitude, payload.reason
        )
        return LateCheckInResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request submission failed: {str(e)}"
        )

@router.post("/approve-request", response_model=ApprovalResponse)
def approve_request(
    payload: ApprovalRequest,
    team_lead: User = Depends(get_current_team_lead),
    db: Session = Depends(get_db)
):
    """Team Lead approves or rejects late check-in request"""
    try:
        result = approve_late_check_in(
            db, team_lead, payload.attendance_id, payload.approve, payload.comment
        )
        return ApprovalResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval failed: {str(e)}"
        )

@router.get("/history", response_model=list[AttendanceResponse])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 30
):
    """Get user's attendance history"""
    records = get_user_attendance_history(db, current_user.id, limit)
    return [AttendanceResponse(**{
        "id": r.id,
        "user_id": r.user_id,
        "status": r.status,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "distance_from_home": r.distance_from_home,
        "is_late_request": r.is_late_request,
        "late_request_reason": r.late_request_reason,
        "approved_by": r.approved_by,
        "approved_at": r.approved_at,
        "created_at": r.created_at
    }) for r in records]

@router.get("/pending-approvals", response_model=list[AttendanceResponse])
def get_pending(
    team_lead: User = Depends(get_current_team_lead),
    db: Session = Depends(get_db)
):
    """Get all pending late check-in requests (Team Lead only)"""
    records = get_pending_approvals(db)
    return [AttendanceResponse(**{
        "id": r.id,
        "user_id": r.user_id,
        "status": r.status,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "distance_from_home": r.distance_from_home,
        "is_late_request": r.is_late_request,
        "late_request_reason": r.late_request_reason,
        "approved_by": r.approved_by,
        "approved_at": r.approved_at,
        "created_at": r.created_at
    }) for r in records]
