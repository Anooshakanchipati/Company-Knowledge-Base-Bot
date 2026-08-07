import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import engine
from app.routers import admin, auth, chat


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Company Knowledge Base Bot API",
    description="Backend API for the Company Knowledge Base Bot",
    version="1.0.0",
)

cors_origins = os.getenv(
    "CORS_ORIGINS",
    (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "https://company-knowledge-base-bot-1.onrender.com"
    ),
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://company-knowledge-base-bot-1.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {
        "message": "Company Knowledge Base Bot API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
    }