from pydantic import BaseModel, EmailStr
from app.models.notification import NotificationType, NotificationStatus, NotificationPriority
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType = NotificationType.EMAIL
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_type: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    status: Optional[NotificationStatus] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None

class NotificationInDB(NotificationBase):
    id: int
    user_id: int
    status: NotificationStatus
    retry_count: int
    max_retries: int
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Notification(NotificationInDB):
    pass

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    status: NotificationStatus
    action_type: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Templates for common notification types
class EmailNotificationTemplate(BaseModel):
    subject: str
    body: str
    html_body: Optional[str] = None
    
class NotificationTemplate(BaseModel):
    action_type: str
    title_template: str
    message_template: str
    email_template: Optional[EmailNotificationTemplate] = None
    priority: NotificationPriority = NotificationPriority.NORMAL

class BulkNotificationCreate(BaseModel):
    user_ids: list[int]
    title: str
    message: str
    type: NotificationType = NotificationType.EMAIL
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_type: str
    scheduled_at: Optional[datetime] = None
