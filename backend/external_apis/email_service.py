import os

import resend
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if not RESEND_API_KEY:
    raise RuntimeError("RESEND_API_KEY is not set")

resend.api_key = RESEND_API_KEY


def send_email(
    recipient: str,
    subject: str,
    html: str,
):
    return resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": recipient,
        "subject": subject,
        "html": html,
    })