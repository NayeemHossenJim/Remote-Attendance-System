from app.models.user import User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from datetime import datetime, timedelta
from app.core.security import (verify_password, hash_password, generate_password_reset_token)

def authenticate(db: Session, office_id: str, password: str):
    """Authenticate user and return user object"""
    user = db.query(User).filter(User.office_id == office_id).first()
    if not user:
        return None
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    if not verify_password(password, user.password_hash):
        return None
    return user

def register_user(
    db: Session, 
    office_id: str, 
    password: str, 
    latitude: float, 
    longitude: float,
    email: str = None,
    role: str = "employee"
):
    """Register a new user with GPS location"""
    existing_user = db.query(User).filter(User.office_id == office_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Office ID already registered")
    user = User(
        office_id=office_id,
        password_hash=hash_password(password),
        email=email,
        home_latitude=latitude,
        home_longitude=longitude,
        allowed_radius_m=settings.DEFAULT_RADIUS_METERS,
        role=role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def request_password_reset(db: Session, office_id: str, email: str = None):
    """Generate password reset token"""
    user = db.query(User).filter(User.office_id == office_id).first()
    if not user:
        return {"message": "If the office ID exists, a password reset link has been sent."}
    
    if email and user.email and user.email != email:
        return {"message": "If the office ID exists, a password reset link has been sent."}
    reset_token = generate_password_reset_token()
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(
        hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
    )
    
    db.commit()
    return {
        "message": "Password reset token generated",
        "reset_token": reset_token
    }

def reset_password(db: Session, token: str, new_password: str):
    """Reset password using token"""
    user = db.query(User).filter(
        User.password_reset_token == token,
        User.password_reset_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    
    db.commit()
    return {"message": "Password reset successfully"}
