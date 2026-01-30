import os
from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.api import auth, attendance
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes (must be before static files)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])

if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_root():
    """Serve frontend HTML"""
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"message": "Remote Attendance System API use /docs for API documentation", "docs": "/docs"}

