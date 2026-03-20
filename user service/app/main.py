from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import router
import os

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service API",
    description="User profile management service for Payment Processing & Fraud Detection System",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React
        "http://localhost:5173",      # Vite
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "user-service",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    return {
        "message": "User Service API",
        "docs": "/docs",
        "health": "/health"
    }