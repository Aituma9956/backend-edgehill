# EdgeHill PGR Management System

A comprehensive Postgraduate Research (PGR) student management system built with FastAPI for Edge Hill University.

## Features

### Core Functionality
- **Role-based Authentication**: 12 different user roles with appropriate permissions
- **Student Management**: Complete student lifecycle from registration to graduation
- **Supervision Management**: Director of Studies and supervisor assignment and tracking
- **Viva Management**: Viva team proposal, approval, scheduling, and outcome tracking
- **Timeline Management**: Milestone tracking for proposal, progression, and final stages
- **Annual Appraisals**: Student and DoS submissions with approval workflow
- **Document Submissions**: File upload and review system for various submission types
- **Comprehensive Reporting**: Dashboard and detailed reports for administrators

### User Roles
1. **System Administrator** - Full system access and configuration
2. **Academic Administrator/Registry Staff** - Student registration and academic records
3. **Graduate School Board of Studies (GBoS) Administrator** - Viva and progress oversight
4. **Graduate School Board of Studies (GBoS) Approver** - Approval workflows
5. **Director of Studies (DoS)** - Student supervision and mentoring
6. **Supervisor** - Student supervision records and progress tracking
7. **Student/PGR** - Personal academic record and submissions
8. **Examiner** - Viva participation and reporting
9. **Ethics Committee Administrator** - Ethics approval processing
10. **International Office Staff** - International student management
11. **Research Office Staff** - Research project oversight
12. **Finance/Funding Administrator** - Funding and grant management
13. **Human Resources Representative** - GTA and employment processing

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with role-based access control
- **Migration**: Alembic for database migrations
- **Testing**: Pytest with comprehensive test coverage
- **Validation**: Pydantic for data validation

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /token` - User authentication
- `GET /me` - Get current user info

### Students (`/api/v1/students`)
- `POST /` - Create student record
- `GET /` - List students with filtering
- `GET /{student_number}` - Get specific student
- `PUT /{student_number}` - Update student record
- `DELETE /{student_number}` - Delete student record

### Supervisors (`/api/v1/supervisors`)
- `POST /` - Create supervisor record
- `GET /` - List supervisors
- `GET /{supervisor_id}` - Get specific supervisor
- `PUT /{supervisor_id}` - Update supervisor
- `DELETE /{supervisor_id}` - Delete supervisor

### Registrations (`/api/v1/registrations`)
- `POST /` - Create registration
- `GET /` - List registrations
- `GET /{registration_id}` - Get specific registration
- `PUT /{registration_id}` - Update registration
- `POST /{registration_id}/extension` - Request extension
- `POST /{registration_id}/extension/approve` - Approve extension

### Viva Teams (`/api/v1/viva-teams`)
- `POST /` - Propose viva team
- `GET /` - List viva teams
- `GET /{viva_team_id}` - Get specific viva team
- `PUT /{viva_team_id}` - Update viva team
- `POST /{viva_team_id}/approve` - Approve viva team
- `POST /{viva_team_id}/reject` - Reject viva team
- `POST /{viva_team_id}/schedule` - Schedule viva
- `POST /{viva_team_id}/outcome` - Submit viva outcome

### Timelines (`/api/v1/timelines`)
- `POST /` - Create timeline milestone
- `GET /student/{student_number}` - Get student timeline
- `PUT /{timeline_id}` - Update timeline

### Appraisals (`/api/v1/appraisals`)
- `POST /` - Create appraisal
- `GET /student/{student_number}` - Get student appraisals
- `PUT /{appraisal_id}/student-submission` - Student submission
- `PUT /{appraisal_id}/dos-submission` - DoS submission
- `POST /{appraisal_id}/approve` - Approve appraisal

### Submissions (`/api/v1/submissions`)
- `POST /` - Create submission
- `GET /` - List submissions
- `GET /{submission_id}` - Get specific submission
- `POST /{submission_id}/upload` - Upload file
- `PUT /{submission_id}` - Update submission
- `POST /{submission_id}/approve` - Approve submission
- `POST /{submission_id}/reject` - Reject submission

### Reports (`/api/v1/reports`)
- `GET /students` - Student summary report
- `GET /registrations` - Registration report
- `GET /vivas` - Viva report
- `GET /appraisals` - Appraisal report
- `GET /submissions` - Submission report
- `GET /dashboard` - Dashboard summary

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EdgeHill Project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update database credentials and other settings

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Development

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Code Structure
```
app/
├── api/           # API endpoints
├── core/          # Core utilities (auth, config, dependencies)
├── db/            # Database configuration
├── models/        # SQLAlchemy models
└── main.py        # FastAPI application

tests/             # Test files
alembic/           # Database migrations
```

## PGR Workflow

### 1. Initial Student Information Entry
- University School Admin captures PGR student details
- Basic student profile created in system

### 2. University Registration
- Student/Registration Office completes university registration
- Registration record created with deadlines and status tracking

### 3. Timeline Definition
- Director of Studies defines timeline for proposal, progression, and final stages
- Timeline milestones saved in student's record

### 4. Supervisory Team Setup
- GBoS Admin assigns Director of Studies and up to 2 Internal Supervisors
- Maximum of 3 persons total in supervisory team

### 5. Registration Viva Team Proposal
- DoS proposes 2 internal supervisors as viva panel
- Only Edge Hill staff can be selected

### 6. Viva Proposal Approval
- GBoS Approver approves or rejects proposed viva team

### 7. Student Document Submission
- Student uploads registration viva documents
- Document tracking and review workflow

### 8. Viva Scheduling & Execution
- GBoS Admin schedules viva and invites examiners
- DoS conducts viva and submits recommendation
- Approver reviews and approves final outcome

### 9. Annual Appraisal
- PGR Student and DoS submit yearly appraisal
- Review and approval process with iteration if unsatisfactory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.
