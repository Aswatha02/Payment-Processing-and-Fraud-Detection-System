import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock
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
    yield
    Base.metadata.drop_all(bind=engine_test)

@patch("app.routes.validate_token", new_callable=AsyncMock)
@patch("app.routes.create_wallet_for_user", new_callable=AsyncMock)
def test_create_user_and_submit_kyc(mock_create_wallet, mock_validate):
    # Mock user token validation
    mock_validate.return_value = {
        "valid": True,
        "data": {"user_id": 1, "role": "USER"}
    }
    
    # 1. Create a User Profile
    response = client.post("/users/", headers={"Authorization": "Bearer fake-token"}, json={
        "user_id": 1,
        "full_name": "John Doe",
        "phone": "+1234567890"
    })
    assert response.status_code == 201

    # 2. Check KYC is NOT_SUBMITTED (default set in routes.py during creation)
    response = client.get("/users/me", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json()["kyc_status"] == "NOT_SUBMITTED"
    
    # 3. Submit KYC
    response = client.post("/users/kyc/submit", headers={"Authorization": "Bearer fake-token"}, json={
        "kyc_document_url": "https://s3.example.com/doc.pdf"
    })
    assert response.status_code == 200

    # 4. Check status is SUBMITTED
    response = client.get("/users/me", headers={"Authorization": "Bearer fake-token"})
    assert response.json()["kyc_status"] == "SUBMITTED"

@patch("app.routes.validate_token", new_callable=AsyncMock)
def test_admin_approve_kyc(mock_validate):
    # Mock Admin token validation
    mock_validate.return_value = {
        "valid": True,
        "data": {"user_id": 99, "role": "ADMIN"}
    }
    
    response = client.patch("/users/1/kyc", headers={"Authorization": "Bearer fake-admin-token"}, json={
        "kyc_status": "VERIFIED"
    })
    assert response.status_code == 200

    
@patch("app.routes.validate_token", new_callable=AsyncMock)
@patch("app.routes.create_wallet_for_user", new_callable=AsyncMock)
def test_admin_reject_kyc(mock_create_wallet, mock_validate):
    # Create another user for rejection testing
    mock_validate.return_value = {"valid": True, "data": {"user_id": 2, "role": "USER"}}
    client.post("/users/", headers={"Authorization": "Bearer fake-token-2"}, json={
        "user_id": 2, "full_name": "Jane Doe"
    })
    
    # Mock Admin token validation
    mock_validate.return_value = {"valid": True, "data": {"user_id": 99, "role": "ADMIN"}}
    
    response = client.patch("/users/2/kyc", headers={"Authorization": "Bearer fake-admin-token"}, json={
        "kyc_status": "REJECTED",
        "rejection_reason": "Blurry image"
    })
    assert response.status_code == 200
    
    # Assert rejection reason is stored
    response = client.get("/users/2", headers={"Authorization": "Bearer fake-admin-token"})
    assert response.json()["kyc_status"] == "REJECTED"
    assert response.json()["kyc_rejection_reason"] == "Blurry image"

@patch("app.routes.validate_token", new_callable=AsyncMock)
def test_kyc_reject_requires_reason(mock_validate):
    mock_validate.return_value = {"data": {"user_id": 99, "role": "ADMIN"}}
    # It should fail pydantic validation
    response = client.patch("/users/2/kyc", headers={"Authorization": "Bearer fake-admin-token"}, json={
        "kyc_status": "REJECTED"
        # Missing rejection_reason
    })
    assert response.status_code == 422
