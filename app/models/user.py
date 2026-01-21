from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    office_id = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    home_latitude = Column(Float, nullable=False)
    home_longitude = Column(Float, nullable=False)
    allowed_radius_m = Column(Integer, default=10)
