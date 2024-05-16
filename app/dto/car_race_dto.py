from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from beanie import PydanticObjectId

from app.dto.common import BaseResponseData, BasePaginationResponseData, BeanieDocumentWithId


class CarRaceResponseData(BeanieDocumentWithId):
    car_race_name: str
    description: Optional[str]
    library_id: PydanticObjectId
    bonus_time_setting: float
    penalty_time_setting: float
    additional_materials: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class CarRaceResponse(BaseResponseData):
    data: CarRaceResponseData


class CarRacePaginationResponseData(BasePaginationResponseData):
    items: List[CarRaceResponseData]


class CarRacePaginationResponse(BaseResponseData):
    data: CarRacePaginationResponseData


class CarRacePutRequest(BaseModel):
    car_race_name: str
    description: Optional[str]
    library_id: str
    bonus_time_setting: float
    penalty_time_setting: float
    additional_materials: Optional[List[str]]