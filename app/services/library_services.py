import logging
from typing import List
from datetime import datetime
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.models.library import Library
from app.models.question import Question
from app.dto.library_dto import LibraryResponseData
from app.helpers.exceptions import NotFoundException, BadRequestException

_logger = logging.getLogger(__name__)


class LibraryService:
    @staticmethod
    async def list_libraries(user_id: str, page: int, limit: int) -> List[LibraryResponseData]:
        skip = limit * (page - 1)
        query = Library.find({"user_id": PydanticObjectId(user_id)})
        total = await query.count()
        libraries = await query.skip(skip).limit(limit).sort(-Library.id).project(LibraryResponseData).to_list()
        return libraries, total
    
    @staticmethod
    async def get_library_by_id(user_id: str, library_id: str) -> LibraryResponseData:
        query = Library.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(library_id)})
        library = await query.project(LibraryResponseData)
        if not library:
            raise NotFoundException("Library not found")
        return library
    
    @staticmethod
    async def create(user_id: str, new_library: dict):
        library = Library(**new_library, user_id=PydanticObjectId(user_id), created_at=datetime.now(), updated_at=datetime.now())
        try:
            await library.save()
        except DuplicateKeyError:
            raise BadRequestException("Library already exists")
        _logger.info(f"New library created: {library.library_name}")

    @staticmethod
    async def copy(user_id: str, library_id: str) -> LibraryResponseData:
        # Copy library
        original_library = await LibraryService.get_library_by_id(user_id, library_id)
        original_library.id = None
        copied_library = Library(
            user_id=PydanticObjectId(user_id),
            library_name=f"Copy of {original_library.library_name}",
            description=original_library.description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        try:
            await copied_library.save()
        except DuplicateKeyError:
            raise BadRequestException("Library name existed")
        _logger.info(f"New library created: {copied_library.library_name}")
        # Copy questions
        questions = await Question.find({"library_id": PydanticObjectId(library_id)}).to_list()
        current_time = datetime.now()
        for question in questions:
            question.id = None
            question.library_id = copied_library.id
            question.created_at = current_time
            question.updated_at = current_time
            await question.save()
        return copied_library

    @staticmethod
    async def put(user_id: str, library_id: str, update_data: dict) -> LibraryResponseData:
        library = await Library.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(library_id)})
        if not library:
            raise NotFoundException("Library not found")
        update_data.update(updated_at=datetime.now())
        try:
            await library.update({"$set": update_data})
        except DuplicateKeyError:
            raise BadRequestException("Library name existed")
        return LibraryResponseData(**library.dict(), _id=library.id)
    
    @staticmethod
    async def delete(user_id: str, library_id: str) -> None:
        library = await Library.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(library_id)})
        if not library:
            raise NotFoundException("Library not found")
        await Question.find_many({"library_id": library_id}).delete()
        await library.delete()
        _logger.info(f"Library deleted: {library.library_name}")