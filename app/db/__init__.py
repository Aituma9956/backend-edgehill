# Database models
from app.db.base import Base

# Import all models to ensure they're registered with SQLAlchemy
from app.models.user import User
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.student_supervisor import StudentSupervisor
from app.models.registration import Registration
from app.models.timeline import Timeline
from app.models.viva_team import VivaTeam
from app.models.submission import Submission
from app.models.appraisal import Appraisal
