import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock
from app.models import Wallet
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
    
    # Pre-seed database with a couple of wallets for testing
    db = TestingSessionLocal()
    w1 = Wallet(user_id=1, balance=100.0)
    w2 = Wallet(user_id=2, balance=50.0)
    db.add_all([w1, w2])
    db.commit()
    db.close()
    
    yield
    Base.metadata.drop_all(bind=engine_test)

@patch("app.routes.validate_user_token", new_callable=AsyncMock)
@patch("app.routes.check_kyc_status", new_callable=AsyncMock)
def test_deposit_success(mock_kyc, mock_validate):
    mock_validate.return_value = {"user_id": 1}
    mock_kyc.return_value = None  # means KYC is verified
    
    response = client.post("/wallet/deposit", headers={"Authorization": "Bearer fake-token"}, json={
        "user_id": 1,
        "amount": 50.0
    })
    assert response.status_code == 200
    assert response.json()["balance"] == 150.0

@patch("app.routes.validate_user_token", new_callable=AsyncMock)
@patch("app.routes.check_kyc_status", new_callable=AsyncMock)
def test_deposit_negative_amount(mock_kyc, mock_validate):
    mock_validate.return_value = {"user_id": 1}
    response = client.post("/wallet/deposit", headers={"Authorization": "Bearer fake-token"}, json={
        "user_id": 1,
        "amount": -20.0
    })
    assert response.status_code == 400

@patch("app.routes.validate_user_token", new_callable=AsyncMock)
@patch("app.routes.check_kyc_status", new_callable=AsyncMock)
def test_withdraw_success(mock_kyc, mock_validate):
    mock_validate.return_value = {"user_id": 1}
    response = client.post("/wallet/withdraw", headers={"Authorization": "Bearer fake-token"}, json={
        "user_id": 1,
        "amount": 30.0
    })
    assert response.status_code == 200
    assert response.json()["balance"] == 120.0

@patch("app.routes.validate_user_token", new_callable=AsyncMock)
@patch("app.routes.check_kyc_status", new_callable=AsyncMock)
def test_withdraw_insufficient_balance(mock_kyc, mock_validate):
    mock_validate.return_value = {"user_id": 2}
    response = client.post("/wallet/withdraw", headers={"Authorization": "Bearer fake-token-2"}, json={
        "user_id": 2,
        "amount": 1000.0
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance"

@patch("app.routes.validate_user_token", new_callable=AsyncMock)
@patch("app.routes.check_kyc_status", new_callable=AsyncMock)
def test_transfer_success(mock_kyc, mock_validate):
    mock_validate.return_value = {"user_id": 1}
    # Transfer 20 from User 1 to User 2. User 1 has 120, User 2 has 50.
    response = client.post("/wallet/transfer", headers={"Authorization": "Bearer fake-token"}, json={
        "user_id": 1,
        "recipient_id": 2,
        "amount": 20.0
    })
    assert response.status_code == 200
    assert response.json()["balance"] == 100.0  # User 1 balance
    
    # Check User 2 balance via a get_balance call disguised as User 2
    mock_validate.return_value = {"user_id": 2}
    resp2 = client.get("/wallet/2/balance", headers={"Authorization": "Bearer fake-token-2"})
    assert resp2.status_code == 200
    assert resp2.json()["balance"] == 70.0

@patch("app.routes.validate_user_token", new_callable=AsyncMock)
@patch("app.routes.check_kyc_status", new_callable=AsyncMock)
def test_transfer_insufficient_balance(mock_kyc, mock_validate):
    mock_validate.return_value = {"user_id": 2} # Balance is 70
    response = client.post("/wallet/transfer", headers={"Authorization": "Bearer fake-token-2"}, json={
        "user_id": 2,
        "recipient_id": 1,
        "amount": 5000.0
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance"

@patch("app.routes.validate_user_token", new_callable=AsyncMock)
@patch("app.routes.check_kyc_status", new_callable=AsyncMock)
def test_transfer_to_self(mock_kyc, mock_validate):
    mock_validate.return_value = {"user_id": 1}
    response = client.post("/wallet/transfer", headers={"Authorization": "Bearer fake-token"}, json={
        "user_id": 1,
        "recipient_id": 1,
        "amount": 10.0
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot transfer to self"
