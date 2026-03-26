from fastapi import FastAPI
from .database import Base, engine
from .routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Audit Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
