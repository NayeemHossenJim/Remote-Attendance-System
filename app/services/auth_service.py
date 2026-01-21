from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password

def authenticate(db: Session, office_id: str, password: str):
    user = db.query(User).filter(User.office_id == office_id).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
