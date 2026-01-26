from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.models.user import User
from app.core.time import check_time, is_within_check_in_window
from app.core.geo import haversine
from app.core.config import settings
from fastapi import HTTPException

def check_in(db: Session, user: User, lat: float, lng: float):
    """
    Main check-in function following the flowchart logic:
    - If 08:00-09:30: Check GPS, mark PRESENT/ABSENT
    - If after 09:30: Mark ABSENT, enable late request
    """
    now = datetime.utcnow()
    time_state = check_time(now)
    
    # Check if user already checked in today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_checkin = db.query(Attendance).filter(
        Attendance.user_id == user.id,
        Attendance.created_at >= today_start
    ).first()
    
    if existing_checkin and existing_checkin.status == "PRESENT":
        return {
            "status": "PRESENT",
            "message": "You have already checked in today",
            "distance_from_home": existing_checkin.distance_from_home,
            "check_in_enabled": False,
            "can_request_present": False
        }
    
    # Calculate distance from home
    if user.home_latitude and user.home_longitude:
        distance = haversine(
            lat, lng,
            user.home_latitude,
            user.home_longitude
        )
    else:
        distance = None
    
    # Flowchart logic: 08:00 - 09:30
    if time_state == "ON_TIME":
        if distance is None:
            status = "ABSENT"
            message = "Home location not set. Please contact administrator."
            check_in_enabled = False
        elif distance <= user.allowed_radius_m:
            # Location matches - Mark Present
            status = "PRESENT"
            message = "Check-in successful! You are marked as present."
            check_in_enabled = True
        else:
            # Location doesn't match - Mark Absent
            status = "ABSENT"
            message = f"Location mismatch. You are {distance:.0f}m away from your registered location (allowed: {user.allowed_radius_m}m)."
            check_in_enabled = False
        
        # Create attendance record
        attendance = Attendance(
            user_id=user.id,
            status=status,
            latitude=lat,
            longitude=lng,
            distance_from_home=distance,
            is_late_request=False
        )
        db.add(attendance)
        db.commit()
        
        return {
            "status": status,
            "message": message,
            "distance_from_home": distance,
            "check_in_enabled": check_in_enabled,
            "can_request_present": False
        }
    
    # Flowchart logic: After 09:30
    elif time_state == "LATE":
        # Mark as absent automatically
        status = "ABSENT"
        message = "Check-in window has passed (08:00-09:30). You are marked as absent. You can request to be marked present."
        
        # Create attendance record marked as absent
        attendance = Attendance(
            user_id=user.id,
            status=status,
            latitude=lat,
            longitude=lng,
            distance_from_home=distance,
            is_late_request=False
        )
        db.add(attendance)
        db.commit()
        
        return {
            "status": status,
            "message": message,
            "distance_from_home": distance,
            "check_in_enabled": False,
            "can_request_present": True
        }
    
    # Before check-in window
    else:
        return {
            "status": "BEFORE_WINDOW",
            "message": f"Check-in window opens at {settings.CHECK_IN_START_HOUR:02d}:{settings.CHECK_IN_START_MINUTE:02d}",
            "distance_from_home": distance,
            "check_in_enabled": False,
            "can_request_present": False
        }

def submit_late_check_in_request(
    db: Session, 
    user: User, 
    lat: float, 
    lng: float, 
    reason: str
):
    """Submit late check-in request (after 09:30)"""
    now = datetime.utcnow()
    time_state = check_time(now)
    
    if time_state != "LATE":
        raise HTTPException(
            status_code=400, 
            detail="Late check-in requests can only be submitted after the check-in window"
        )
    
    # Check if there's already a pending request today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_request = db.query(Attendance).filter(
        Attendance.user_id == user.id,
        Attendance.created_at >= today_start,
        Attendance.is_late_request == True,
        Attendance.status == "PENDING"
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="You already have a pending late check-in request for today"
        )
    
    # Calculate distance
    distance = None
    if user.home_latitude and user.home_longitude:
        distance = haversine(
            lat, lng,
            user.home_latitude,
            user.home_longitude
        )
    
    # Create pending request
    attendance = Attendance(
        user_id=user.id,
        status="PENDING",
        latitude=lat,
        longitude=lng,
        distance_from_home=distance,
        is_late_request=True,
        late_request_reason=reason
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return {
        "message": "Late check-in request submitted. Pending Team Lead approval.",
        "request_id": attendance.id,
        "status": "PENDING"
    }

def approve_late_check_in(
    db: Session,
    team_lead: User,
    attendance_id: int,
    approve: bool,
    comment: str = None
):
    """Team Lead approves or rejects late check-in request"""
    if team_lead.role != "team_lead":
        raise HTTPException(status_code=403, detail="Only team leads can approve requests")
    
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id,
        Attendance.is_late_request == True,
        Attendance.status == "PENDING"
    ).first()
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Pending request not found")
    
    if approve:
        attendance.status = "PRESENT"
        attendance.approved_by = team_lead.id
        attendance.approved_at = datetime.utcnow()
        message = "Late check-in request approved. Employee marked as present."
    else:
        attendance.status = "ABSENT"
        attendance.approved_by = team_lead.id
        attendance.approved_at = datetime.utcnow()
        if comment:
            attendance.late_request_reason = f"{attendance.late_request_reason}\n[Rejected: {comment}]"
        message = "Late check-in request rejected. Employee remains marked as absent."
    
    db.commit()
    
    return {
        "message": message,
        "attendance_id": attendance_id,
        "status": attendance.status
    }

def get_user_attendance_history(db: Session, user_id: int, limit: int = 30) -> List[Attendance]:
    """Get user's attendance history"""
    return db.query(Attendance).filter(
        Attendance.user_id == user_id
    ).order_by(Attendance.created_at.desc()).limit(limit).all()

def get_pending_approvals(db: Session, team_lead_id: int = None) -> List[Attendance]:
    """Get all pending late check-in requests"""
    query = db.query(Attendance).filter(
        Attendance.is_late_request == True,
        Attendance.status == "PENDING"
    )
    
    if team_lead_id:
        # Get requests for team members (simplified - in production, add team relationship)
        query = query
    
    return query.order_by(Attendance.created_at.desc()).all()
