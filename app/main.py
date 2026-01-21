from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api import auth, attendance
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

app.include_router(auth.router, prefix="/auth")
app.include_router(attendance.router, prefix="/attendance")

