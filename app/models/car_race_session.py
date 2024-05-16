from typing import Optional, List
from beanie import PydanticObjectId
from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel, RootEnum

class SessionStatus(str, RootEnum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    ENDED = "ENDED"

class CarRaceSession(RootModel):
    class Collection:
        name = "car_race_session"
        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING),
                    ("car_race_session_name", ASCENDING),
                ],
                unique=True
            ),
        ]

    user_id: PydanticObjectId
    car_race_id: PydanticObjectId
    car_race_session_name: str
    session_status: SessionStatus
    result: dict