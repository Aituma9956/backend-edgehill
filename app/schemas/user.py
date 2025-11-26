from pydantic import BaseModel
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    # Core Roles
    SYSTEM_ADMIN = "system_admin"
    ACADEMIC_ADMIN = "academic_admin"
    GBOS_ADMIN = "gbos_admin"
    GBOS_APPROVER = "gbos_approver"
    DOS = "dos"
    SUPERVISOR = "supervisor"
    STUDENT = "student"
    EXAMINER = "examiner"
    ETHICS_ADMIN = "ethics_admin"
    INTERNATIONAL_OFFICE = "international_office"
    RESEARCH_OFFICE = "research_office"
    FINANCE_ADMIN = "finance_admin"
    HR_REPRESENTATIVE = "hr_representative"
    USER = "user"  # Generic user role

class UserBase(BaseModel):
    username: str
    email: str
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None

class AdminUserUpdate(BaseModel):
    """Admin-only user update schema that includes role changes"""
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
