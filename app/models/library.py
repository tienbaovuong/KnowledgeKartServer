from typing import Optional
from beanie import PydanticObjectId
from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel

class Library(RootModel):
    class Collection:
        name = "library"
        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING),
                    ("library_name", ASCENDING),
                ],
                unique=True
            ),
        ]

    user_id: PydanticObjectId
    library_name: str
    description: Optional[str]