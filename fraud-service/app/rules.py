from datetime import datetime

recent_transactions = {}

def check_large_amount(amount):
    return amount > 10000

def check_high_frequency(user_id):
    now = datetime.utcnow()

    if user_id not in recent_transactions:
        recent_transactions[user_id] = []

    recent_transactions[user_id].append(now)

    recent_transactions[user_id] = [
        t for t in recent_transactions[user_id]
        if (now - t).seconds < 60
    ]

    return len(recent_transactions[user_id]) > 5

def check_night_time():
    hour = datetime.utcnow().hour
    # Night time defined as 1 AM to 5 AM UTC
    return 1 <= hour <= 5

def evaluate_fraud(user_id, amount):
    risk_score = 0
    reasons = []

    if check_large_amount(amount):
        risk_score += 50
        reasons.append("Large amount")

    if check_high_frequency(user_id):
        risk_score += 30
        reasons.append("High frequency")

    if check_night_time():
        risk_score += 20
        reasons.append("Odd hour")

    status = "APPROVED"
    if risk_score >= 50:
        status = "FLAGGED"

    return {
        "risk_score": risk_score,
        "status": status,
        "reasons": reasons
    }
