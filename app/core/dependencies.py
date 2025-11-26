from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRole
from app.core.config import settings
from typing import List

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials

        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            valid_roles = ", ".join([role.value for role in UserRole])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Your role: '{current_user.role}'. Valid roles for this endpoint: {', '.join(allowed_roles)}. All available system roles: {valid_roles}"
            )
        return current_user
    return role_checker

def require_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.SYSTEM_ADMIN.value:
        valid_roles = ", ".join([role.value for role in UserRole])
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"System administrator access required. Your role: '{current_user.role}'. Required role: 'system_admin'. All available system roles: {valid_roles}"
        )
    return current_user

def require_gbos_admin(current_user: User = Depends(get_current_active_user)):
    allowed_roles = [UserRole.SYSTEM_ADMIN.value, UserRole.GBOS_ADMIN.value]
    if current_user.role not in allowed_roles:
        valid_roles = ", ".join([role.value for role in UserRole])
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"GBoS administrator access required. Your role: '{current_user.role}'. Required roles: {', '.join(allowed_roles)}. All available system roles: {valid_roles}"
        )
    return current_user

def require_dos(current_user: User = Depends(get_current_active_user)):
    allowed_roles = [UserRole.SYSTEM_ADMIN.value, UserRole.GBOS_ADMIN.value, UserRole.DOS.value]
    if current_user.role not in allowed_roles:
        valid_roles = ", ".join([role.value for role in UserRole])
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Director of Studies access required. Your role: '{current_user.role}'. Required roles: {', '.join(allowed_roles)}. All available system roles: {valid_roles}"
        )
    return current_user

def require_supervisor_or_above(current_user: User = Depends(get_current_active_user)):
    allowed_roles = [UserRole.SYSTEM_ADMIN.value, UserRole.GBOS_ADMIN.value, UserRole.DOS.value, UserRole.SUPERVISOR.value]
    if current_user.role not in allowed_roles:
        valid_roles = ", ".join([role.value for role in UserRole])
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Supervisor access or higher required. Your role: '{current_user.role}'. Required roles: {', '.join(allowed_roles)}. All available system roles: {valid_roles}"
        )
    return current_user
