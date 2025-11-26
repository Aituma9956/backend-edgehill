from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user import UserRole

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    # Role is automatically set to 'student' - not user-configurable

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class AdminPasswordReset(BaseModel):
    """Admin-only password reset schema"""
    new_password: str
