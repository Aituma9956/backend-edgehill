from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from app.models.notification import Notification, NotificationStatus, NotificationPriority, NotificationType
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate, 
    NotificationUpdate, 
    Notification as NotificationSchema,
    BulkNotificationCreate,
    NotificationTemplate
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    
    # Notification templates for common actions
    TEMPLATES = {
        "submission_created": NotificationTemplate(
            action_type="submission_created",
            title_template="New Submission Created",
            message_template="A new submission '{submission_title}' has been created by {student_name}.",
            priority=NotificationPriority.NORMAL
        ),
        "submission_approved": NotificationTemplate(
            action_type="submission_approved",
            title_template="Submission Approved",
            message_template="Your submission '{submission_title}' has been approved.",
            priority=NotificationPriority.HIGH
        ),
        "submission_rejected": NotificationTemplate(
            action_type="submission_rejected",
            title_template="Submission Requires Revision",
            message_template="Your submission '{submission_title}' requires revision. Comments: {comments}",
            priority=NotificationPriority.HIGH
        ),
        "viva_scheduled": NotificationTemplate(
            action_type="viva_scheduled",
            title_template="Viva Examination Scheduled",
            message_template="Your viva examination has been scheduled for {viva_date} at {location}.",
            priority=NotificationPriority.URGENT
        ),
        "appraisal_due": NotificationTemplate(
            action_type="appraisal_due",
            title_template="Appraisal Due Soon",
            message_template="Your appraisal is due on {due_date}. Please complete it as soon as possible.",
            priority=NotificationPriority.HIGH
        ),
        "supervisor_assigned": NotificationTemplate(
            action_type="supervisor_assigned",
            title_template="Supervisor Assigned",
            message_template="You have been assigned a new supervisor: {supervisor_name} ({role}).",
            priority=NotificationPriority.NORMAL
        ),
        "password_reset": NotificationTemplate(
            action_type="password_reset",
            title_template="Password Reset",
            message_template="Your password has been reset by an administrator.",
            priority=NotificationPriority.HIGH
        )
    }
    
    @staticmethod
    def create_notification(db: Session, notification_data: NotificationCreate, current_user: User) -> NotificationSchema:
        """Create a new notification"""
        # Verify the user exists
        target_user = db.query(User).filter(User.id == notification_data.user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # If no recipient email provided, use user's email
        if not notification_data.recipient_email:
            notification_data.recipient_email = target_user.email
        
        # Convert metadata to JSON string if provided
        extra_data_str = json.dumps(notification_data.metadata) if notification_data.metadata else None
        
        db_notification = Notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            action_type=notification_data.action_type,
            related_entity_type=notification_data.related_entity_type,
            related_entity_id=notification_data.related_entity_id,
            priority=notification_data.priority,
            recipient_email=notification_data.recipient_email,
            recipient_phone=notification_data.recipient_phone,
            scheduled_at=notification_data.scheduled_at or datetime.utcnow(),
            extra_data=extra_data_str
        )
        
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        
        # Try to send immediately if it's scheduled for now or past
        if db_notification.scheduled_at <= datetime.utcnow():
            NotificationService._send_notification(db, db_notification)
        
        return NotificationSchema.from_orm(db_notification)
    
    @staticmethod
    def create_from_template(
        db: Session, 
        action_type: str, 
        user_id: int, 
        template_data: Dict[str, Any],
        current_user: User,
        notification_type: NotificationType = NotificationType.EMAIL
    ) -> NotificationSchema:
        """Create notification from predefined template"""
        if action_type not in NotificationService.TEMPLATES:
            raise HTTPException(status_code=400, detail=f"Unknown notification template: {action_type}")
        
        template = NotificationService.TEMPLATES[action_type]
        
        # Format the title and message with provided data
        try:
            title = template.title_template.format(**template_data)
            message = template.message_template.format(**template_data)
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing template data: {e}")
        
        notification_data = NotificationCreate(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            action_type=action_type,
            priority=template.priority,
            related_entity_type=template_data.get('entity_type'),
            related_entity_id=template_data.get('entity_id'),
            metadata=template_data
        )
        
        return NotificationService.create_notification(db, notification_data, current_user)
    
    @staticmethod
    def get_user_notifications(
        db: Session, 
        user_id: int, 
        current_user: User,
        skip: int = 0, 
        limit: int = 100,
        status: Optional[NotificationStatus] = None
    ) -> List[NotificationSchema]:
        """Get notifications for a user"""
        # Users can only see their own notifications, admins can see anyone's
        if current_user.role not in ["system_admin"] and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view these notifications")
        
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if status:
            query = query.filter(Notification.status == status)
        
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        return [NotificationSchema.from_orm(notification) for notification in notifications]
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int, current_user: User) -> NotificationSchema:
        """Mark notification as delivered/read"""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Users can only mark their own notifications as read
        if current_user.role not in ["system_admin"] and current_user.id != notification.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this notification")
        
        notification.status = NotificationStatus.DELIVERED
        notification.delivered_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
        
        return NotificationSchema.from_orm(notification)
    
    @staticmethod
    def retry_failed_notifications(db: Session, current_user: User) -> Dict[str, int]:
        """Retry sending failed notifications (admin only)"""
        if current_user.role != "system_admin":
            raise HTTPException(status_code=403, detail="Only system administrators can retry notifications")
        
        failed_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.FAILED,
            Notification.retry_count < Notification.max_retries
        ).all()
        
        success_count = 0
        failed_count = 0
        
        for notification in failed_notifications:
            if NotificationService._send_notification(db, notification):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "retried": len(failed_notifications),
            "successful": success_count,
            "failed": failed_count
        }
    
    @staticmethod
    def create_bulk_notification(
        db: Session, 
        bulk_data: BulkNotificationCreate, 
        current_user: User
    ) -> List[NotificationSchema]:
        """Create notifications for multiple users"""
        if current_user.role not in ["system_admin", "academic_admin", "gbos_admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to send bulk notifications")
        
        notifications = []
        for user_id in bulk_data.user_ids:
            try:
                notification_data = NotificationCreate(
                    user_id=user_id,
                    type=bulk_data.type,
                    title=bulk_data.title,
                    message=bulk_data.message,
                    action_type=bulk_data.action_type,
                    priority=bulk_data.priority,
                    scheduled_at=bulk_data.scheduled_at
                )
                notification = NotificationService.create_notification(db, notification_data, current_user)
                notifications.append(notification)
            except Exception as e:
                logger.error(f"Failed to create notification for user {user_id}: {e}")
                continue
        
        return notifications
    
    @staticmethod
    def _send_notification(db: Session, notification: Notification) -> bool:
        """Internal method to send notification"""
        try:
            if notification.type == NotificationType.EMAIL:
                return NotificationService._send_email(db, notification)
            elif notification.type == NotificationType.SMS:
                return NotificationService._send_sms(db, notification)
            elif notification.type == NotificationType.IN_APP:
                # In-app notifications are just stored in database
                notification.status = NotificationStatus.DELIVERED
                notification.sent_at = datetime.utcnow()
                notification.delivered_at = datetime.utcnow()
                db.commit()
                return True
            else:
                logger.warning(f"Unsupported notification type: {notification.type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {e}")
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            notification.retry_count += 1
            db.commit()
            return False
    
    @staticmethod
    def _send_email(db: Session, notification: Notification) -> bool:
        """Send email notification"""
        try:
            # Email configuration (should be in settings)
            smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = getattr(settings, 'SMTP_PORT', 587)
            smtp_username = getattr(settings, 'SMTP_USERNAME', '')
            smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
            from_email = getattr(settings, 'FROM_EMAIL', smtp_username)
            
            if not smtp_username or not smtp_password:
                logger.warning("Email configuration not set up")
                return False
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = notification.recipient_email
            msg['Subject'] = notification.title
            
            # Email body
            body = f"""
            {notification.message}
            
            ---
            EdgeHill PGR Management System
            Action Type: {notification.action_type}
            Sent: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            # Update notification status
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Email notification {notification.id} sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification {notification.id}: {e}")
            raise
    
    @staticmethod
    def _send_sms(db: Session, notification: Notification) -> bool:
        """Send SMS notification (placeholder - implement with SMS service)"""
        try:
            # Placeholder for SMS implementation
            # You would integrate with services like Twilio, AWS SNS, etc.
            logger.info(f"SMS notification {notification.id} would be sent to {notification.recipient_phone}")
            
            # For now, just mark as sent
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification {notification.id}: {e}")
            raise
    
    @staticmethod
    def _extract_template_variables(title_template: str, message_template: str) -> List[str]:
        """Extract required variables from template strings"""
        import re
        variables = set()
        
        # Find all {variable_name} patterns
        for template in [title_template, message_template]:
            matches = re.findall(r'\{([^}]+)\}', template)
            variables.update(matches)
        
        return list(variables) 