from pydantic import BaseModel

class CheckInRequest(BaseModel):
    latitude: float
    longitude: float
