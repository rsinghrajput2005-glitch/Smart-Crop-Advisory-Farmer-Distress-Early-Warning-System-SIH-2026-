import secrets
from datetime import datetime, timedelta, timezone
import os
import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.external_apis.email_service import send_email
from passlib.context import CryptContext
from fastapi import HTTPException
from backend.database.models import User, EmailOTP, EmailVerification

from jose import jwt
from datetime import datetime, timedelta, timezone

OTP_EXPIRY_MINUTES = 5


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    return bcrypt.hashpw(
        otp.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def request_registration_otp(
    db: Session,
    email: str,
) -> None:

    # 1. Check whether the email is already registered
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise ValueError("Email is already registered")

    # 2. Generate OTP
    otp = generate_otp()

    # 3. Hash OTP
    otp_hash = hash_otp(otp)

    # 4. Calculate expiry
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=OTP_EXPIRY_MINUTES)
    )

    # 5. Check whether an OTP already exists
    existing_otp = db.scalar(
        select(EmailOTP).where(EmailOTP.email == email)
    )

    if existing_otp:
        existing_otp.otp_hash = otp_hash
        existing_otp.expires_at = expires_at
        existing_otp.attempts = 0
        existing_otp.created_at = datetime.now(timezone.utc)
    else:
        new_otp = EmailOTP(
            email=email,
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0,
            created_at=datetime.now(timezone.utc),
        )

        db.add(new_otp)

    db.commit()

    # 6. Send plaintext OTP to the user's email
    send_email(
        recipient=email,
        subject="SIH2026 Email Verification",
        html=f"""
        <h2>Email Verification</h2>
        <p>Your verification OTP is:</p>
        <h1>{otp}</h1>
        <p>This OTP expires in {OTP_EXPIRY_MINUTES} minutes.</p>
        """,
    )


def verify_registration_otp(
    db,
    email: str,
    otp: str
):
    otp_record = db.scalar(
        select(EmailOTP)
        .where(EmailOTP.email == email)
    )

    if not otp_record:
        raise HTTPException(status_code=404, detail="No OTP found for this email")

    if otp_record.expires_at < datetime.now(timezone.utc):
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired")

    if otp_record.attempts >= 5:
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=400, detail="Maximum OTP attempts exceeded")

    if not bcrypt.checkpw(otp.encode(), otp_record.otp_hash.encode()):
        otp_record.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # OTP is valid — delete it and record that this email is verified
    db.delete(otp_record)

    existing_verification = db.scalar(
        select(EmailVerification).where(EmailVerification.email == email)
    )
    if not existing_verification:
        db.add(EmailVerification(email=email))

    db.commit()

    return True

def complete_registration_service(
    db: Session,
    email: str,
    username: str,
    password: str
):
    verification = db.scalar(
        select(EmailVerification).where(
            EmailVerification.email == email
        )
    )

    if not verification:
        raise HTTPException(
            status_code=400,
            detail="Email has not been verified"
        )

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.delete(verification)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration completed successfully"
    }






SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set")


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def login_service(
    db: Session,
    email: str,
    password: str,
):
    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


