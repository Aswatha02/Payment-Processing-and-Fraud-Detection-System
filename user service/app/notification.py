import os
import requests

NOTIFICATION_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8006")

def send_notification(user_id, message, type):
    try:
        requests.post(
            f"{NOTIFICATION_URL}/notifications/",
            json={
                "user_id": user_id,
                "message": message,
                "type": type
            },
            timeout=2.0
        )
    except Exception as e:
        print(f"Failed to send notification to User {user_id}: {e}")
