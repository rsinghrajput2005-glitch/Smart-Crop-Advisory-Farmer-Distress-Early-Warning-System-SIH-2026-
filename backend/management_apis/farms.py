from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.database.models import Farm
from backend.database.database import get_db
from backend.helper_apis.jwt_auth import get_current_user
from backend.service_apis.farm_service import create_farm


router = APIRouter(
    prefix="/farms",
    tags=["Farms"],
)


class FarmCreateRequest(BaseModel):
    latitude: float
    longitude: float


@router.post("/")
def add_farm(
    data: FarmCreateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    return create_farm(
        db=db,
        user_id=user_id,
        latitude=data.latitude,
        longitude=data.longitude,
    )


@router.get("/")
def get_farms(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    farms = db.scalars(
        select(Farm).where(Farm.user_id == current_user)
    ).all()

    return farms

@router.get("/{farm_id}")
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    farm = db.scalar(
        select(Farm).where(
            Farm.id == farm_id,
            Farm.user_id == current_user,
        )
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    return farm

@router.delete("/{farm_id}")
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    farm = db.scalar(
        select(Farm).where(
            Farm.id == farm_id,
            Farm.user_id == current_user,
        )
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    db.delete(farm)
    db.commit()

    return {
        "message": "Farm deleted successfully"
    }