from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (
    auth, students, supervisors, registrations, viva_teams, 
    timelines, appraisals, submissions, reports, student_supervisors, notifications
)
from app.db.session import engine
from app.db.base import Base
import os
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EdgeHill PGR Management System",
    description="Postgraduate Research Student Management System for Edge Hill University",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(supervisors.router, prefix="/api/v1/supervisors", tags=["Supervisors"])
app.include_router(student_supervisors.router, prefix="/api/v1/student-supervisors", tags=["Student-Supervisor Assignments"])
app.include_router(registrations.router, prefix="/api/v1/registrations", tags=["Registrations"])
app.include_router(viva_teams.router, prefix="/api/v1/viva-teams", tags=["Viva Teams"])
app.include_router(timelines.router, prefix="/api/v1/timelines", tags=["Timelines"])
app.include_router(appraisals.router, prefix="/api/v1/appraisals", tags=["Appraisals"])
app.include_router(submissions.router, prefix="/api/v1/submissions", tags=["Submissions"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])

@app.get("/")
async def root():
    return {"message": "EdgeHill PGR Management System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
