from typing import Optional, List
from beanie import PydanticObjectId
from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel

class CarRace(RootModel):
    class Collection:
        name = "car_race"
        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING),
                    ("car_race_name", ASCENDING),
                ],
                unique=True
            ),
        ]

    user_id: PydanticObjectId
    car_race_name: str
    description: Optional[str]
    library_id: PydanticObjectId
    bonus_time_setting: float
    penalty_time_setting: float
    additional_materials: Optional[List[str]]