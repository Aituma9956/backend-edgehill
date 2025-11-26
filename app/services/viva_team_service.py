from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from fastapi import HTTPException
from app.models.viva_team import VivaTeam, VivaStatus, VivaStage
from app.models.user import User
from app.models.supervisor import Supervisor
from app.schemas.viva_team import VivaTeamCreate, VivaTeamUpdate, VivaTeam as VivaTeamSchema

class VivaTeamService:
    @staticmethod
    def propose_viva_team(db: Session, viva_team: VivaTeamCreate, current_user: User) -> VivaTeamSchema:
        """Propose a new viva team"""
        if current_user.role not in ["gbos_admin", "dos", "system_admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to propose viva teams")
        
        # Get the viva team data and set the correct status and metadata
        viva_team_data = viva_team.dict()
        
        # Remove zero or None values for foreign key fields
        if viva_team_data.get('internal_examiner_1_id') in [0, None]:
            viva_team_data['internal_examiner_1_id'] = None
        if viva_team_data.get('internal_examiner_2_id') in [0, None]:
            viva_team_data['internal_examiner_2_id'] = None
        
        # Validate that supervisor IDs exist if provided
        if viva_team_data.get('internal_examiner_1_id'):
            examiner_1 = db.query(Supervisor).filter(Supervisor.supervisor_id == viva_team_data['internal_examiner_1_id']).first()
            if not examiner_1:
                raise HTTPException(status_code=400, detail=f"Internal examiner 1 with ID {viva_team_data['internal_examiner_1_id']} not found")
        
        if viva_team_data.get('internal_examiner_2_id'):
            examiner_2 = db.query(Supervisor).filter(Supervisor.supervisor_id == viva_team_data['internal_examiner_2_id']).first()
            if not examiner_2:
                raise HTTPException(status_code=400, detail=f"Internal examiner 2 with ID {viva_team_data['internal_examiner_2_id']} not found")
        
        # Ensure stage is the correct enum type for the model
        if 'stage' in viva_team_data:
            stage_value = viva_team_data['stage']
            # Convert to model enum using the string value
            if hasattr(stage_value, 'value'):
                viva_team_data['stage'] = VivaStage(stage_value.value)
            else:
                viva_team_data['stage'] = VivaStage(stage_value)
        
        viva_team_data.update({
            "status": VivaStatus.PROPOSED,
            "proposed_by": current_user.id,
            "proposed_date": date.today()
        })
        
        db_viva_team = VivaTeam(**viva_team_data)
        db.add(db_viva_team)
        db.commit()
        db.refresh(db_viva_team)
        return VivaTeamSchema.from_orm(db_viva_team)
    
    @staticmethod
    def get_viva_teams(db: Session, current_user: User, skip: int = 0, limit: int = 100,
                      student_number: Optional[str] = None, stage: Optional[str] = None,
                      status: Optional[str] = None) -> List[VivaTeamSchema]:
        """Get viva teams with filtering and authorization"""
        query = db.query(VivaTeam)

        if student_number:
            query = query.filter(VivaTeam.student_number.ilike(f"%{student_number}%"))
        
        if stage:
            # Convert string to enum if needed
            try:
                stage_enum = VivaStage(stage) if isinstance(stage, str) else stage
                query = query.filter(VivaTeam.stage == stage_enum)
            except ValueError:
                pass  # Invalid stage value, ignore filter
            
        if status:
            # Convert string to enum if needed
            try:
                status_enum = VivaStatus(status) if isinstance(status, str) else status
                query = query.filter(VivaTeam.status == status_enum)
            except ValueError:
                pass  # Invalid status value, ignore filter

        # Students can only see their own viva teams
        if current_user.role == "student":
            query = query.filter(VivaTeam.student_number == current_user.username)
        
        viva_teams = query.offset(skip).limit(limit).all()
        return [VivaTeamSchema.from_orm(vt) for vt in viva_teams]
    
    @staticmethod
    def get_viva_team_by_id(db: Session, viva_team_id: int, current_user: User) -> VivaTeamSchema:
        """Get viva team by ID with authorization check"""
        viva_team = db.query(VivaTeam).filter(VivaTeam.id == viva_team_id).first()
        if not viva_team:
            raise HTTPException(status_code=404, detail="Viva team not found")

        # Students can only view their own viva teams
        if current_user.role == "student" and viva_team.student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to view this viva team")
        
        return VivaTeamSchema.from_orm(viva_team)
    
    @staticmethod
    def update_viva_team(db: Session, viva_team_id: int, viva_team_update: VivaTeamUpdate) -> VivaTeamSchema:
        """Update viva team information"""
        db_viva_team = db.query(VivaTeam).filter(VivaTeam.id == viva_team_id).first()
        if not db_viva_team:
            raise HTTPException(status_code=404, detail="Viva team not found")
        
        update_data = viva_team_update.dict(exclude_unset=True)
        
        # Remove zero values for foreign key fields
        if 'internal_examiner_1_id' in update_data and update_data['internal_examiner_1_id'] == 0:
            update_data['internal_examiner_1_id'] = None
        if 'internal_examiner_2_id' in update_data and update_data['internal_examiner_2_id'] == 0:
            update_data['internal_examiner_2_id'] = None
        
        # Validate that supervisor IDs exist if provided
        if update_data.get('internal_examiner_1_id'):
            examiner_1 = db.query(Supervisor).filter(Supervisor.supervisor_id == update_data['internal_examiner_1_id']).first()
            if not examiner_1:
                raise HTTPException(status_code=400, detail=f"Internal examiner 1 with ID {update_data['internal_examiner_1_id']} not found")
        
        if update_data.get('internal_examiner_2_id'):
            examiner_2 = db.query(Supervisor).filter(Supervisor.supervisor_id == update_data['internal_examiner_2_id']).first()
            if not examiner_2:
                raise HTTPException(status_code=400, detail=f"Internal examiner 2 with ID {update_data['internal_examiner_2_id']} not found")
        
        # Convert schema enums to model enums if present
        if 'stage' in update_data:
            stage_value = update_data['stage']
            if hasattr(stage_value, 'value'):
                update_data['stage'] = VivaStage(stage_value.value)
            else:
                update_data['stage'] = VivaStage(stage_value)
                
        if 'status' in update_data:
            status_value = update_data['status']
            if hasattr(status_value, 'value'):
                update_data['status'] = VivaStatus(status_value.value)
            else:
                update_data['status'] = VivaStatus(status_value)
        
        for field, value in update_data.items():
            setattr(db_viva_team, field, value)
        
        db.commit()
        db.refresh(db_viva_team)
        return VivaTeamSchema.from_orm(db_viva_team)
    
    @staticmethod
    def approve_viva_team(db: Session, viva_team_id: int, current_user: User) -> VivaTeamSchema:
        """Approve a viva team"""
        # Only gbos admin can approve viva teams
        if current_user.role not in ["gbos_admin", "system_admin", "gbos_approver"]:
            raise HTTPException(status_code=403, detail="Not authorized to approve viva teams")
        
        viva_team = db.query(VivaTeam).filter(VivaTeam.id == viva_team_id).first()
        if not viva_team:
            raise HTTPException(status_code=404, detail="Viva team not found")
        
        viva_team.status = VivaStatus.APPROVED
        viva_team.approval_date = datetime.now()
        viva_team.approved_by = current_user.id
        db.commit()
        db.refresh(viva_team)
        return VivaTeamSchema.from_orm(viva_team)
    
    @staticmethod
    def reject_viva_team(db: Session, viva_team_id: int, reason: str) -> VivaTeamSchema:
        """Reject a viva team"""
        viva_team = db.query(VivaTeam).filter(VivaTeam.id == viva_team_id).first()
        if not viva_team:
            raise HTTPException(status_code=404, detail="Viva team not found")
        
        viva_team.status = VivaStatus.REJECTED
        # Note: rejection_reason field doesn't exist in model, you may need to add it
        # viva_team.rejection_reason = reason
        db.commit()
        db.refresh(viva_team)
        return VivaTeamSchema.from_orm(viva_team)
    
    @staticmethod
    def schedule_viva(db: Session, viva_team_id: int, scheduled_date: date, location: str) -> VivaTeamSchema:
        """Schedule a viva for an approved team"""
        viva_team = db.query(VivaTeam).filter(VivaTeam.id == viva_team_id).first()
        if not viva_team:
            raise HTTPException(status_code=404, detail="Viva team not found")
            
        if viva_team.status != VivaStatus.APPROVED:
            raise HTTPException(status_code=400, detail="Viva team must be approved before scheduling")
        
        viva_team.status = VivaStatus.SCHEDULED
        viva_team.scheduled_date = scheduled_date
        viva_team.location = location
        db.commit()
        db.refresh(viva_team)
        return VivaTeamSchema.from_orm(viva_team)
    
    @staticmethod
    def submit_viva_outcome(db: Session, viva_team_id: int, outcome: str, outcome_notes: str) -> VivaTeamSchema:
        """Submit viva outcome"""
        viva_team = db.query(VivaTeam).filter(VivaTeam.id == viva_team_id).first()
        if not viva_team:
            raise HTTPException(status_code=404, detail="Viva team not found")
        
        viva_team.status = VivaStatus.COMPLETED
        viva_team.outcome = outcome
        viva_team.outcome_notes = outcome_notes
        viva_team.actual_date = date.today()
        db.commit()
        db.refresh(viva_team)
        return VivaTeamSchema.from_orm(viva_team)
