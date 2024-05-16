from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.dto.common import BaseResponseData, BasePaginationResponseData, BeanieDocumentWithId


class LibraryResponseData(BeanieDocumentWithId):
    library_name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class LibraryResponse(BaseResponseData):
    data: LibraryResponseData


class LibraryPaginationResponseData(BasePaginationResponseData):
    items: List[LibraryResponseData]


class LibraryPaginationResponse(BaseResponseData):
    data: LibraryPaginationResponseData


class LibraryPutRequest(BaseModel):
    library_name: str
    description: Optional[str]