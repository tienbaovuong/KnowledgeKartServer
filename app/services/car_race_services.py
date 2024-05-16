import logging
from typing import List
from datetime import datetime
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.models.library import Library
from app.models.car_race import CarRace
from app.dto.car_race_dto import CarRaceResponseData
from app.helpers.exceptions import NotFoundException, BadRequestException

_logger = logging.getLogger(__name__)


class CarRaceService:
    @staticmethod
    async def list_car_races(user_id: str, page: int, limit: int) -> List[CarRaceResponseData]:
        skip = limit * (page - 1)
        query = CarRace.find({"user_id": PydanticObjectId(user_id)})
        total = await query.count()
        car_races = await query.skip(skip).limit(limit).sort(-CarRace.id).project(CarRaceResponseData).to_list()
        return car_races, total
    
    @staticmethod
    async def get_car_race_by_id(user_id: str, car_race_id: str) -> CarRaceResponseData:
        query = CarRace.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(car_race_id)})
        car_race = await query.project(CarRaceResponseData)
        if not car_race:
            raise NotFoundException("Car race not found")
        return car_race
    
    @staticmethod
    async def create(user_id: str, new_car_race: dict):
        library_id = PydanticObjectId(new_car_race["library_id"])
        library = await Library.find_one({"user_id": PydanticObjectId(user_id), "_id": library_id})
        if not library:
            raise NotFoundException("Library not found")
        new_car_race.update({"library_id": library_id})
        car_race = CarRace(**new_car_race, user_id=PydanticObjectId(user_id), created_at=datetime.now(), updated_at=datetime.now())
        try:
            await car_race.save()
        except DuplicateKeyError:
            raise BadRequestException("Car race already exists")
        _logger.info(f"New car race created: {car_race.car_race_name}")

    @staticmethod
    async def put(user_id: str, car_race_id: str, update_data: dict) -> CarRaceResponseData:
        car_race = await CarRace.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(car_race_id)})
        if not car_race:
            raise NotFoundException("Car race not found")
        try:
            update_data.update(updated_at=datetime.now())
            await  car_race.update({"$set": update_data})
        except DuplicateKeyError:
            raise BadRequestException("Car race name existed")
        return CarRaceResponseData(**car_race.dict(), _id=car_race.id)
    
    @staticmethod
    async def delete(user_id: str, car_race_id: str) -> None:
        car_race = await CarRace.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(car_race_id)})
        if not car_race:
            raise NotFoundException("Car race not found")
        await car_race.delete()
        _logger.info(f"Car race deleted: {car_race.car_race_name}")