# backend/model/models.py
from pydantic import BaseModel

class LoginRequest(BaseModel):
    basic_username: str
    basic_password: str
    portal_username: str
    portal_password: str