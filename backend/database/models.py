from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, BigInteger, Column, func

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

'''
Mapping
PostgreSQL              SQLAlchemy

email_otps
├── id              →   EmailOTP.id
├── email           →   EmailOTP.email
├── otp_hash        →   EmailOTP.otp_hash
├── expires_at      →   EmailOTP.expires_at
└── used            →   EmailOTP.used
'''
from sqlalchemy import Boolean, DateTime, Integer, String, BigInteger, Column, func



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )



class EmailOTP(Base):
    __tablename__ = "email_otps"

    email: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    otp_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

class EmailVerification(Base):
    __tablename__ = "email_verifications"

    email = Column(String, primary_key=True)
    verified_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # Farmer-chosen label for this farm, e.g. "North field", "Home plot"
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    latitude: Mapped[float] = mapped_column(
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        nullable=False,
    )

    # Human-readable place name, e.g. "Bhubaneswar, Odisha" (reverse-geocoded
    # or typed by the user) — optional since it's just a display convenience.
    location_name: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    crop: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    growth_stage: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    # State name, used for mandi price lookups
    state: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

