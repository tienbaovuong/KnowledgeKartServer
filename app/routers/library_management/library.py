from fastapi import APIRouter, Depends, Query

from app.dto.common import BaseResponse
from app.dto.library_dto import LibraryPaginationResponse, LibraryPaginationResponseData, LibraryResponse, LibraryPutRequest
from app.helpers.auth_helpers import get_current_user
from app.helpers.exceptions import BadRequestException
from app.services.library_services import LibraryService

router = APIRouter(tags=['Library'], prefix='/library')


@router.get(
    '/list',
    response_model=LibraryPaginationResponse,
)
async def get_list_libraries(
    user_id: str = Depends(get_current_user),
    page: int = Query(1),
    limit: int = Query(10),
):
    items, total = await LibraryService.list_libraries(
        user_id=user_id,
        page=page,
        limit=limit,
    )

    return LibraryPaginationResponse(
        message="Get list library successfully",
        data=LibraryPaginationResponseData(
            items=items,
            total=total,
        )
    )


@router.get(
    '/{library_id}',
)
async def get_library_by_id(
    library_id: str,
    user_id: str = Depends(get_current_user),
):
    library_data = await LibraryService.get_library_by_id(
        user_id=user_id,
        library_id=library_id,
    )

    return LibraryResponse(
        message="Get library successfully",
        data=library_data
    )


@router.post(
    '/create',
)
async def create_library(
    create_library_data: LibraryPutRequest,
    user_id: str = Depends(get_current_user),
):
    await LibraryService.create(
        user_id=user_id,
        new_library=create_library_data.dict(),
    )
    
    return BaseResponse(
        message="Created library successfully"
    )


@router.post(
    '/copy',
)
async def copy_library(
    user_id: str = Depends(get_current_user),
    library_id: str = Query(''),
):
    if not library_id:
        raise BadRequestException("Library id is required")
    copied_library = await LibraryService.copy(
        user_id=user_id,
        library_id=library_id,
    )

    return BaseResponse(
        message="Copied library successfully",
    )


@router.put(
    '/{library_id}',
)
async def update_library_by_id(
    library_id: str,
    update_library_data: LibraryPutRequest,
    user_id: str = Depends(get_current_user),
):
    updated_data = await LibraryService.put(
        user_id=user_id,
        library_id=library_id,
        update_data=update_library_data.dict(),
    )
    return LibraryResponse(
        message="Updated library successfully",
        data=updated_data
    )


@router.delete(
    '/{library_id}',
)
async def delete_library_by_id(
    library_id: str,
    user_id: str = Depends(get_current_user),
):
    await LibraryService.delete(
        user_id=user_id,
        library_id=library_id,
    )
    return BaseResponse(
        message="Deleted library successfully"
    )