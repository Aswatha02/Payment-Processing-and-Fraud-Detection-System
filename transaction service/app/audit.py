import urllib.request
import json
import os

AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://localhost:8005")

def log_audit(service_name: str, action: str, user_id: int | None = None, details: str | None = None):
    try:
        data = {
            "service_name": service_name,
            "action": action,
            "user_id": user_id,
            "details": details
        }
        req = urllib.request.Request(f"{AUDIT_SERVICE_URL}/audit/", method="POST")
        req.add_header('Content-Type', 'application/json')
        urllib.request.urlopen(req, data=json.dumps(data).encode('utf-8'), timeout=2)
    except Exception as e:
        print(f"Failed to send audit log: {e}")
