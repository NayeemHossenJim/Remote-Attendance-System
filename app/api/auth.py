from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest
from app.services.auth_service import authenticate
from app.db.session import get_db

router = APIRouter()

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, payload.office_id, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id}
