from sqlalchemy.orm import Session

from backend.database.models import Farm


def create_farm(
    db: Session,
    user_id: int,
    latitude: float,
    longitude: float,
):
    farm = Farm(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return {
        "message": "Farm created successfully",
        "farm_id": farm.id,
        "latitude": farm.latitude,
        "longitude": farm.longitude,
    }






