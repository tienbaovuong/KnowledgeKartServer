from typing import Optional, List, Union
from datetime import datetime
from pydantic import BaseModel
from beanie import PydanticObjectId

from app.dto.common import BaseResponseData, BasePaginationResponseData, BeanieDocumentWithId
from app.models.question import QuestionType, QuestionChoice


class QuestionResponseData(BeanieDocumentWithId):
    library_id: PydanticObjectId
    question: Union[str, List[str]]
    question_type: QuestionType = QuestionType.MULTIPLE
    choices: Optional[List[QuestionChoice]]
    answer: Union[str, List[str]]
    created_at: datetime
    updated_at: datetime


class QuestionResponse(BaseResponseData):
    data: QuestionResponseData


class QuestionPaginationResponseData(BasePaginationResponseData):
    items: List[QuestionResponseData]


class QuestionPaginationResponse(BaseResponseData):
    data: QuestionPaginationResponseData


class QuestionPutRequest(BaseModel):
    question: Union[str, List[str]]
    question_type: QuestionType = QuestionType.MULTIPLE
    choices: Optional[List[QuestionChoice]]
    answer: Union[str, List[str]]