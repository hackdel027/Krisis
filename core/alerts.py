"""Gmail alert delivery using OAuth2 credentials supplied by the operator."""

from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Any

import requests


GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def send_gmail_alert(access_token: str, recipient: str, subject: str, body: str) -> dict[str, Any]:
    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode().rstrip("=")
    response = requests.post(
        GMAIL_SEND_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        json={"raw": raw_message},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()
