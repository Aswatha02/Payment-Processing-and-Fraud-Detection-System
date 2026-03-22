import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

client = TestClient(app)

engine_test = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    os.environ["ADMIN_SECRET"] = "test-secret"
    yield
    Base.metadata.drop_all(bind=engine_test)

def test_admin_register_success():
    response = client.post("/auth/admin/register", json={
        "username": "admin1",
        "email": "admin1@test.com",
        "password": "Password123!",
        "admin_secret": "test-secret"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"

def test_admin_register_invalid_secret():
    response = client.post("/auth/admin/register", json={
        "username": "admin2",
        "email": "admin2@test.com",
        "password": "Password123!",
        "admin_secret": "wrong-secret"
    })
    assert response.status_code == 403

def test_admin_login():
    response = client.post("/auth/admin/login", json={
        "email": "admin1@test.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "ADMIN"

def test_user_cannot_login_as_admin():
    # Register normal user
    client.post("/auth/register", json={
        "username": "user1",
        "email": "user1@test.com",
        "password": "Password123!"
    })
    
    # Try admin login
    response = client.post("/auth/admin/login", json={
        "email": "user1@test.com",
        "password": "Password123!"
    })
    assert response.status_code == 403
