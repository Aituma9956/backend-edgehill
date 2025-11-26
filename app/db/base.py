from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here so Alembic can detect them
from app.models.user import User
from app.models.notification import Notification
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.student_supervisor import StudentSupervisor
from app.models.registration import Registration
from app.models.submission import Submission
from app.models.timeline import Timeline
from app.models.appraisal import Appraisal
from app.models.viva_team import VivaTeam
