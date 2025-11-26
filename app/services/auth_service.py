from sqlalchemy.orm import Session
from app.models.user import User 
from app.schemas.user import User as UserSchema
from app.schemas.auth import RegisterRequest
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.core.config import settings

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        """Authenticate a user with username and password"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
    
    @staticmethod
    def create_user(db: Session, user_data: RegisterRequest) -> UserSchema:
        """Create a new user"""
        # Check if username already exists
        if db.query(User).filter(User.username == user_data.username).first():
            raise ValueError("Username already registered")
        
        # Check if email already exists
        if db.query(User).filter(User.email == user_data.email).first():
            raise ValueError("Email already registered")
        
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role if hasattr(user_data, 'role') and user_data.role else "student",
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            department=user_data.department
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserSchema.from_orm(db_user)
    
    @staticmethod
    def create_access_token_for_user(user: User):
        """Create access token for authenticated user"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, 
            expires_delta=access_token_expires
        )
        return access_token
    
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: dict) -> UserSchema:
        """Update user information"""
        from app.schemas.user import UserUpdate
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if username is being changed and if it already exists
        if 'username' in user_data and user_data['username'] != user.username:
            if db.query(User).filter(User.username == user_data['username']).first():
                raise ValueError("Username already exists")
        
        # Check if email is being changed and if it already exists
        if 'email' in user_data and user_data['email'] != user.email:
            if db.query(User).filter(User.email == user_data['email']).first():
                raise ValueError("Email already exists")
        
        # Update user fields
        for field, value in user_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return UserSchema.from_orm(user)
    
    @staticmethod
    def admin_update_user(db: Session, user_id: int, user_data: dict, admin_user: User) -> UserSchema:
        """Admin-only method to update any user's information including role"""
        from app.schemas.user import UserUpdate
        
        # Only system admins can update user roles and sensitive information
        if admin_user.role != "system_admin":
            raise ValueError("Only system administrators can update user information")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if username is being changed and if it already exists
        if 'username' in user_data and user_data['username'] != user.username:
            if db.query(User).filter(User.username == user_data['username']).first():
                raise ValueError("Username already exists")
        
        # Check if email is being changed and if it already exists
        if 'email' in user_data and user_data['email'] != user.email:
            if db.query(User).filter(User.email == user_data['email']).first():
                raise ValueError("Email already exists")
        
        # Update user fields (including role for admin)
        for field, value in user_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return UserSchema.from_orm(user)
    
    @staticmethod
    def get_all_users(db: Session, admin_user: User, skip: int = 0, limit: int = 100) -> list:
        """Get all users (admin only)"""
        if admin_user.role != "system_admin":
            raise ValueError("Only system administrators can view all users")
        
        users = db.query(User).offset(skip).limit(limit).all()
        return [UserSchema.from_orm(user) for user in users]
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int, admin_user: User) -> UserSchema:
        """Get user by ID (admin only)"""
        if admin_user.role != "system_admin":
            raise ValueError("Only system administrators can view user details")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        return UserSchema.from_orm(user)
    
    @staticmethod
    def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user's password"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        # Hash new password and update
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
    
    @staticmethod
    def admin_reset_password(db: Session, user_id: int, new_password: str, admin_user: User) -> bool:
        """Admin-only method to reset any user's password"""
        if admin_user.role != "system_admin":
            raise ValueError("Only system administrators can reset user passwords")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Hash new password and update (no current password verification needed for admin)
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
