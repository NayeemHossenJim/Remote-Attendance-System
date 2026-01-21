from pydantic import BaseModel

class LoginRequest(BaseModel):
    office_id: str
    password: str
