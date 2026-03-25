from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as fraud_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Fraud Detection Service")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fraud_router)

@app.get("/")
async def root():
    return {"message": "Fraud Detection Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fraud-service"}
