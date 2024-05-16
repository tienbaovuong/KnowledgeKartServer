import logging
from typing import List
from datetime import datetime
from beanie import PydanticObjectId

from app.models.library import Library
from app.models.question import Question
from app.dto.question_dto import QuestionResponseData
from app.helpers.exceptions import NotFoundException, BadRequestException

_logger = logging.getLogger(__name__)


class QuestionService:
    @staticmethod
    async def list_questions(user_id: str, library_id: str, page: int, limit: int) -> List[QuestionResponseData]:
        skip = limit * (page - 1)
        query = Question.find({"user_id": PydanticObjectId(user_id), "library_id": PydanticObjectId(library_id)})
        total = await query.count()
        questions = await query.skip(skip).limit(limit).sort(-Question.id).project(QuestionResponseData).to_list()
        return questions, total
    
    @staticmethod
    async def get_question_by_id(user_id: str, question_id: str) -> QuestionResponseData:
        query = Question.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(question_id)})
        question = await query.project(QuestionResponseData)
        if not question:
            raise NotFoundException("Question not found")
        return question
    
    @staticmethod
    async def create(user_id: str, library_id: str, new_question: dict):
        library = await Library.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(library_id)})
        if not library:
            raise NotFoundException("Library not found")
        question = Question(**new_question, user_id=PydanticObjectId(user_id), library_id=PydanticObjectId(library_id), created_at=datetime.now(), updated_at=datetime.now())
        try:
            await question.save()
        except Exception:
            raise BadRequestException("Unknown error")
        _logger.info(f"New question created: {question.question}")

    @staticmethod
    async def copy(user_id: str, question_id: str) -> QuestionResponseData:
        original_question = await QuestionService.get_question_by_id(user_id, question_id)
        original_question.id = None
        copied_question = Question(
            **original_question.dict(),
            user_id=PydanticObjectId(user_id),
        )
        copied_question.created_at = datetime.now()
        copied_question.updated_at = datetime.now()
        try:
            await copied_question.save()
        except Exception:
            raise BadRequestException("Unknown error")
        _logger.info(f"New question created: {copied_question.question}")
        return copied_question

    @staticmethod
    async def put(user_id: str, question_id: str, update_data: dict) -> QuestionResponseData:
        question = await Question.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(question_id)})
        if not question:
            raise NotFoundException("Question not found")
        update_data.update(updated_at=datetime.now())
        await  question.update({"$set": update_data})
        return QuestionResponseData(**question.dict(), _id=question.id)
    
    @staticmethod
    async def delete(user_id: str, question_id: str) -> None:
        question = await Question.find_one({"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(question_id)})
        if not question:
            raise NotFoundException("Question not found")
        await question.delete()
        _logger.info(f"Question deleted: {question.question}")