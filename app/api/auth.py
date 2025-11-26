from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, PasswordChangeRequest, AdminPasswordReset
from app.schemas.user import User as UserResponse, Token, UserUpdate, AdminUserUpdate
from typing import List
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    try:
        db_user = AuthService.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/token", response_model=Token)
def login_for_access_token(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information"""
    try:
        update_data = user_update.dict(exclude_unset=True)
        updated_user = AuthService.update_user(db, current_user.id, update_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.put("/change-password")
def change_password(
    password_data: PasswordChangeRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    try:
        success = AuthService.change_password(
            db, 
            current_user.id, 
            password_data.current_password, 
            password_data.new_password
        )
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to change password")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/admin/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (system admin only)"""
    try:
        users = AuthService.get_all_users(db, current_user, skip, limit)
        return users
    except ValueError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

@router.get("/admin/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (system admin only)"""
    try:
        user = AuthService.get_user_by_id(db, user_id, current_user)
        return user
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=403, detail=str(e))

@router.put("/admin/users/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update any user's information including role (system admin only)"""
    try:
        update_data = user_update.dict(exclude_unset=True)
        updated_user = AuthService.admin_update_user(db, user_id, update_data, current_user)
        return updated_user
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(
            status_code=403 if "administrators" in str(e) else 400,
            detail=str(e)
        )

@router.put("/admin/users/{user_id}/reset-password")
def admin_reset_user_password(
    user_id: int,
    password_reset: AdminPasswordReset,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset user's password (system admin only)"""
    try:
        success = AuthService.admin_reset_password(
            db, 
            user_id, 
            password_reset.new_password, 
            current_user
        )
        if success:
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset password")
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(
            status_code=403 if "administrators" in str(e) else 400,
            detail=str(e)
        )
