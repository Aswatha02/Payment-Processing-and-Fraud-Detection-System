from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import router

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Audit Service API",
    description="Audit logging service",
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
        "http://localhost:8000",  # Auth service
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Audit Service is running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "Audit Service"}