from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LeaveCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str