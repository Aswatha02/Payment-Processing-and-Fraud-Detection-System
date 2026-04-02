from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import router

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service API",
    description="Authentication API for the Payment Processing System",
    version="1.0.0",
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React default
        "http://localhost:5173",      # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",      # Auth service itself
        "http://localhost:8001",      # Audit service
        "http://localhost:8005",      # User service
        "http://localhost:8010",      # Payment service
        "http://localhost:8015",      # Fraud service
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Auth Service is running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "Authentication API"}