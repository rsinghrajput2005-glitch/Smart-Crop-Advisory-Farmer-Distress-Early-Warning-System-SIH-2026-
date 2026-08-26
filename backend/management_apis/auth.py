from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.service_apis.auth_service import (
    request_registration_otp,
    verify_registration_otp,
    complete_registration_service,
    login_service,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class RegistrationRequest(BaseModel):
    email: EmailStr


class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp: str


class CompleteRegistrationRequest(BaseModel):
    email: EmailStr
    username: str
    password: str



class LoginRequest(BaseModel):
    email: EmailStr
    password: str



@router.post("/register")
def register(
    data: RegistrationRequest,
    db: Session = Depends(get_db),
):
    try:
        request_registration_otp(
            db=db,
            email=str(data.email),
        )

        return {
            "message": "OTP sent successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@router.post("/verify-otp")
def verify_otp(
    data: OTPVerificationRequest,
    db: Session = Depends(get_db),
):
    verify_registration_otp(
        db=db,
        email=str(data.email),
        otp=data.otp,
    )

    return {
        "message": "Email verified successfully"
    }


@router.post("/complete-registration")
def complete_registration(
    data: CompleteRegistrationRequest,
    db: Session = Depends(get_db),
):
    return complete_registration_service(
        db=db,
        email=str(data.email),
        username=data.username,
        password=data.password,
    )

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    return login_service(
        db=db,
        email=str(data.email),
        password=data.password,
    )