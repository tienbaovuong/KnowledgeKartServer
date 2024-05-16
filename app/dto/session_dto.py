from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from beanie import PydanticObjectId

from app.dto.common import BaseResponseData, BasePaginationResponseData, BeanieDocumentWithId
from app.models.car_race_session import SessionStatus


class SessionShortResponseData(BeanieDocumentWithId):
    car_race_id: PydanticObjectId
    car_race_session_name: str
    session_status: SessionStatus
    created_at: datetime
    updated_at: datetime


class SessionFullResponseData(BeanieDocumentWithId):
    car_race_id: PydanticObjectId
    car_race_session_name: str
    session_status: SessionStatus
    result: dict
    created_at: datetime
    updated_at: datetime


class SessionResponse(BaseResponseData):
    data: SessionFullResponseData


class SessionPaginationResponseData(BasePaginationResponseData):
    items: List[SessionShortResponseData]


class SessionPaginationResponse(BaseResponseData):
    data: SessionPaginationResponseData


class SessionCreateRequest(BaseModel):
    car_race_id: str
    car_race_session_name: str


class SessionPutRequest(BaseModel):
    car_race_session_name: str
    session_status: SessionStatus