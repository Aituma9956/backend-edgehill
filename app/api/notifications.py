from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationCreate,
    Notification as NotificationResponse,
    BulkNotificationCreate,
    NotificationStatus,
    NotificationType
)

router = APIRouter()

@router.post("/", response_model=NotificationResponse)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new notification"""
    return NotificationService.create_notification(db, notification, current_user)

@router.post("/template/{action_type}", response_model=NotificationResponse)
def create_notification_from_template(
    action_type: str,
    user_id: int,
    template_data: Dict[str, Any],
    notification_type: NotificationType = NotificationType.EMAIL,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create notification from predefined template"""
    return NotificationService.create_from_template(
        db, action_type, user_id, template_data, current_user, notification_type
    )

@router.post("/bulk", response_model=List[NotificationResponse])
def create_bulk_notification(
    bulk_notification: BulkNotificationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create notifications for multiple users (admin only)"""
    return NotificationService.create_bulk_notification(db, bulk_notification, current_user)

@router.get("/user/{user_id}", response_model=List[NotificationResponse])
def get_user_notifications(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[NotificationStatus] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get notifications for a specific user"""
    return NotificationService.get_user_notifications(db, user_id, current_user, skip, limit, status)

@router.get("/me", response_model=List[NotificationResponse])
def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[NotificationStatus] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current user's notifications"""
    return NotificationService.get_user_notifications(db, current_user.id, current_user, skip, limit, status)

@router.put("/{notification_id}/mark-read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark a notification as read/delivered"""
    return NotificationService.mark_as_read(db, notification_id, current_user)

@router.post("/retry-failed")
def retry_failed_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Retry sending failed notifications (admin only)"""
    return NotificationService.retry_failed_notifications(db, current_user)

@router.get("/templates")
def get_available_templates(
    current_user = Depends(get_current_user)
):
    """Get list of available notification templates"""
    if current_user.role not in ["system_admin", "academic_admin", "gbos_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to view templates")
    
    templates = {}
    for action_type, template in NotificationService.TEMPLATES.items():
        templates[action_type] = {
            "title_template": template.title_template,
            "message_template": template.message_template,
            "priority": template.priority,
            "required_data": NotificationService._extract_template_variables(template.title_template, template.message_template)
        }
    
    return templates

# Helper endpoints for common notification scenarios
@router.post("/submission/{submission_id}/approved")
def notify_submission_approved(
    submission_id: int,
    submission_title: str,
    student_user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send submission approved notification"""
    template_data = {
        "submission_title": submission_title,
        "entity_type": "submission",
        "entity_id": submission_id
    }
    
    return NotificationService.create_from_template(
        db, "submission_approved", student_user_id, template_data, current_user
    )

@router.post("/submission/{submission_id}/rejected")
def notify_submission_rejected(
    submission_id: int,
    submission_title: str,
    student_user_id: int,
    comments: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send submission rejected notification"""
    template_data = {
        "submission_title": submission_title,
        "comments": comments,
        "entity_type": "submission",
        "entity_id": submission_id
    }
    
    return NotificationService.create_from_template(
        db, "submission_rejected", student_user_id, template_data, current_user
    )

@router.post("/viva/{viva_id}/scheduled")
def notify_viva_scheduled(
    viva_id: int,
    student_user_id: int,
    viva_date: str,
    location: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send viva scheduled notification"""
    template_data = {
        "viva_date": viva_date,
        "location": location,
        "entity_type": "viva_team",
        "entity_id": viva_id
    }
    
    return NotificationService.create_from_template(
        db, "viva_scheduled", student_user_id, template_data, current_user
    )

@router.post("/supervisor/{supervisor_id}/assigned")
def notify_supervisor_assigned(
    supervisor_id: int,
    student_user_id: int,
    supervisor_name: str,
    role: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send supervisor assigned notification"""
    template_data = {
        "supervisor_name": supervisor_name,
        "role": role,
        "entity_type": "student_supervisor",
        "entity_id": supervisor_id
    }
    
    return NotificationService.create_from_template(
        db, "supervisor_assigned", student_user_id, template_data, current_user
    )
