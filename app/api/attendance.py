from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.attendance import CheckInRequest
from app.services.attendance_service import check_in
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

@router.post("/check-in/{user_id}")
def checkin(user_id: int, payload: CheckInRequest, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    return check_in(db, user, payload.latitude, payload.longitude)
