from typing import Optional, List, Union
from beanie import PydanticObjectId
from pydantic import BaseModel
from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel, RootEnum


class QuestionType(str, RootEnum):
    MULTIPLE = "MULTIPLECHOICE"
    FILL = "FILLINTHEBLANK"


class QuestionChoice(BaseModel):
    choice: str
    feedback: Optional[str]


class Question(RootModel):
    class Collection:
        name = "question"
        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING),
                    ("library_id", ASCENDING),
                ],
            ),
        ]

    user_id: PydanticObjectId
    library_id: PydanticObjectId
    question: Union[str, List[str]]
    question_type: QuestionType
    choices: Optional[List[QuestionChoice]]
    answer: Union[str, List[str]]