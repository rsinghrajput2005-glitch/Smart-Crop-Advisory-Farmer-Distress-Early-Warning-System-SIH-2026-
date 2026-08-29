from sqlalchemy.orm import Session

from backend.database.models import Farm


def create_farm(
    db: Session,
    user_id: int,
    name: str,
    latitude: float,
    longitude: float,
    location_name: str | None = None,
    crop: str | None = None,
    growth_stage: str | None = None,
    state: str | None = None,
):
    farm = Farm(
        user_id=user_id,
        name=name,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        crop=crop,
        growth_stage=growth_stage,
        state=state,
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return farm