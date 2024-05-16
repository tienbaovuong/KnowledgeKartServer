import logging
from typing import List
from datetime import datetime
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from fastapi import BackgroundTasks

from app.services.live_session_services import start_session_in_background
from app.models.car_race_session import CarRaceSession, SessionStatus
from app.models.car_race import CarRace
from app.dto.session_dto import SessionFullResponseData, SessionShortResponseData
from app.helpers.exceptions import NotFoundException, BadRequestException

_logger = logging.getLogger(__name__)


class SessionService:
    @staticmethod
    async def list_sessions(user_id: str, page: int, limit: int) -> List[SessionShortResponseData]:
        skip = limit * (page - 1)
        query = CarRaceSession.find({"user_id": PydanticObjectId(user_id)})
        total = await query.count()
        car_races = await query.skip(skip).limit(limit).sort(-CarRaceSession.id).project(SessionShortResponseData).to_list()
        return car_races, total
    
    @staticmethod
    async def get_session_by_id(user_id: str, session_id: str) -> SessionFullResponseData:
        query = CarRaceSession.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(session_id)})
        session = await query.project(SessionFullResponseData)
        if not session:
            raise NotFoundException("Session not found")
        return session
    
    @staticmethod
    async def create(user_id: str, new_session: dict, background_tasks: BackgroundTasks):
        car_race_id = PydanticObjectId(new_session["car_race_id"])
        car_race = await CarRace.find_one({"user_id": PydanticObjectId(user_id), "_id": car_race_id})
        if not car_race:
            raise NotFoundException("Car race not found")
        new_session.update({"car_race_id": car_race_id, "session_status": SessionStatus.CREATED, "result": {}})
        session = CarRaceSession(**new_session, user_id=PydanticObjectId(user_id), created_at=datetime.now(), updated_at=datetime.now())
        try:
            new_session = await session.save()
        except DuplicateKeyError:
            raise BadRequestException("Session name existed")
        _logger.info(f"New session created: {session.car_race_session_name}")
        background_tasks.add_task(start_session_in_background, new_session.id, datetime.now())

    @staticmethod
    async def put(user_id: str, session_id: str, update_data: dict) -> SessionFullResponseData:
        session = await CarRaceSession.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(session_id)})
        if not session:
            raise NotFoundException("Session not found")
        update_data.update(updated_at=datetime.now())
        try:
            await session.update({"$set": update_data})
        except DuplicateKeyError:
            raise BadRequestException("Session name existed")
        return SessionFullResponseData(**session.dict(), _id=session.id)
    
    @staticmethod
    async def delete(user_id: str, session_id: str) -> None:
        session = await CarRaceSession.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(session_id)})
        if not session:
            raise NotFoundException("Session not found")
        await session.delete()
        _logger.info(f"Session deleted: {session.car_race_session_name}")