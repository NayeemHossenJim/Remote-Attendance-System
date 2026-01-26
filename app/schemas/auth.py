from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    office_id: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    office_id: str
    role: str

class RegisterRequest(BaseModel):
    office_id: str
    password: str
    email: Optional[EmailStr] = None
    latitude: float
    longitude: float

class RegisterResponse(BaseModel):
    message: str
    user_id: int
    office_id: str

class PasswordResetRequest(BaseModel):
    office_id: str
    email: Optional[str] = None

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class PasswordResetResponse(BaseModel):
    message: str

class UserResponse(BaseModel):
    id: int
    office_id: str
    email: Optional[str]
    role: str
    home_latitude: Optional[float]
    home_longitude: Optional[float]
    allowed_radius_m: int
    
    class Config:
        from_attributes = True
