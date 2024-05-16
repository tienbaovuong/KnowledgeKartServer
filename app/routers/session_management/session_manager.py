from fastapi import APIRouter, Depends, Query, BackgroundTasks

from app.dto.common import BaseResponse
from app.dto.session_dto import SessionPaginationResponseData, SessionPaginationResponse, SessionResponse, SessionPutRequest, SessionCreateRequest
from app.helpers.auth_helpers import get_current_user
from app.services.session_services import SessionService

router = APIRouter(tags=['Car Race Session'], prefix='/session_management')


@router.get(
    '/list',
    response_model=SessionPaginationResponse,
)
async def get_list_sessions(
    user_id: str = Depends(get_current_user),
    page: int = Query(1),
    limit: int = Query(10),
):
    items, total = await SessionService.list_sessions(
        user_id=user_id,
        page=page,
        limit=limit,
    )

    return SessionPaginationResponse(
        message="Get list session successfully",
        data=SessionPaginationResponseData(
            items=items,
            total=total,
        )
    )


@router.get(
    '/{session_id}',
)
async def get_session_by_id(
    session_id: str,
    user_id: str = Depends(get_current_user),
):
    session = await SessionService.get_session_by_id(
        user_id=user_id,
        session_id=session_id,
    )

    return SessionResponse(
        message="Get session successfully",
        data=session
    )


@router.post(
    '/create',
)
async def create_session(
    background_tasks: BackgroundTasks,
    create_session_data: SessionCreateRequest,
    user_id: str = Depends(get_current_user),
):
    await SessionService.create(
        user_id=user_id,
        new_session=create_session_data.dict(),
        background_tasks=background_tasks
    )
    
    return BaseResponse(
        message="Created session successfully"
    )


@router.put(
    '/{session_id}',
)
async def update_session_by_id(
    session_id: str,
    update_session_data: SessionPutRequest,
    user_id: str = Depends(get_current_user),
):
    updated_data = await SessionService.put(
        user_id=user_id,
        session_id=session_id,
        update_data=update_session_data.dict(),
    )
    return SessionResponse(
        message="Updated session successfully",
        data=updated_data
    )


@router.delete(
    '/{session_id}',
)
async def delete_car_race_by_id(
    session_id: str,
    user_id: str = Depends(get_current_user),
):
    await SessionService.delete(
        user_id=user_id,
        session_id=session_id,
    )
    return BaseResponse(
        message="Deleted session successfully"
    )