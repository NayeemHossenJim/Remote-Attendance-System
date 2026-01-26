from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    RegisterRequest, 
    RegisterResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    UserResponse
)
from app.services.auth_service import (
    authenticate, 
    register_user, 
    request_password_reset, 
    reset_password
)
from app.core.security import create_access_token
from app.core.config import settings
from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with office ID, password, and GPS location"""
    try:
        user = register_user(
            db=db,
            office_id=payload.office_id,
            password=payload.password,
            latitude=payload.latitude,
            longitude=payload.longitude,
            email=payload.email
        )
        return RegisterResponse(
            message="Registration successful. Your home location has been saved.",
            user_id=user.id,
            office_id=user.office_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login with office ID and password"""
    user = authenticate(db, payload.office_id, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid office ID or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "office_id": user.office_id, "role": user.role}
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        office_id=user.office_id,
        role=user.role
    )

@router.post("/password-reset-request", response_model=PasswordResetResponse)
def password_reset_request(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset token"""
    result = request_password_reset(db, payload.office_id, payload.email)
    return PasswordResetResponse(message=result["message"])

@router.post("/password-reset", response_model=PasswordResetResponse)
def password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using token"""
    try:
        result = reset_password(db, payload.token, payload.new_password)
        return PasswordResetResponse(message=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password reset failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user.id,
        office_id=current_user.office_id,
        email=current_user.email,
        role=current_user.role,
        home_latitude=current_user.home_latitude,
        home_longitude=current_user.home_longitude,
        allowed_radius_m=current_user.allowed_radius_m
    )
