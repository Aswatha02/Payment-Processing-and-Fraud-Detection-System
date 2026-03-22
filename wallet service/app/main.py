from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import router

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wallet Service API",
    description="Wallet management service for Payment Processing & Fraud Detection System",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
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
        "service": "wallet-service",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    return {
        "message": "Wallet Service API",
        "docs": "/docs",
        "health": "/health"
    }