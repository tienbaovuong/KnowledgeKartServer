from fastapi import APIRouter, Depends, Query

from app.dto.common import BaseResponse
from app.dto.question_dto import QuestionPaginationResponseData, QuestionPaginationResponse, QuestionResponse, QuestionPutRequest
from app.helpers.auth_helpers import get_current_user
from app.helpers.exceptions import BadRequestException
from app.services.question_services import QuestionService

router = APIRouter(tags=['Question'], prefix='/question')


@router.get(
    '/list',
    response_model=QuestionPaginationResponse,
)
async def get_list_questions(
    user_id: str = Depends(get_current_user),
    library_id: str = Query(''),
    page: int = Query(1),
    limit: int = Query(10),
):
    items, total = await QuestionService.list_questions(
        user_id=user_id,
        library_id=library_id,
        page=page,
        limit=limit,
    )

    return QuestionPaginationResponse(
        message="Get list questions successfully",
        data=QuestionPaginationResponseData(
            items=items,
            total=total,
        )
    )


@router.get(
    '/{question_id}',
)
async def get_question_by_id(
    question_id: str,
    user_id: str = Depends(get_current_user),
):
    question = await QuestionService.get_question_by_id(
        user_id=user_id,
        question_id=question_id,
    )

    return QuestionResponse(
        message="Get question data successfully",
        data=question
    )


@router.post(
    '/create',
)
async def create_question(
    create_question_data: QuestionPutRequest,
    user_id: str = Depends(get_current_user),
    library_id: str = Query(""),
):
    await QuestionService.create(
        user_id=user_id,
        library_id=library_id,
        new_question=create_question_data.dict(),
    )
    
    return BaseResponse(
        message="Created question successfully"
    )


@router.post(
    '/copy',
)
async def copy_question(
    user_id: str = Depends(get_current_user),
    question_id: str = Query(''),
):
    if not question_id:
        raise BadRequestException("Question id is required")
    copied_question = await QuestionService.copy(
        user_id=user_id,
        question_id=question_id,
    )

    return BaseResponse(
        message="Copied library successfully",
    )


@router.put(
    '/{question_id}',
)
async def update_question_by_id(
    question_id: str,
    update_question_data: QuestionPutRequest,
    user_id: str = Depends(get_current_user),
):
    updated_data = await QuestionService.put(
        user_id=user_id,
        question_id=question_id,
        update_data=update_question_data.dict(),
    )
    return QuestionResponse(
        message="Updated question successfully",
        data=updated_data
    )


@router.delete(
    '/{question_id}',
)
async def delete_question_by_id(
    question_id: str,
    user_id: str = Depends(get_current_user),
):
    await QuestionService.delete(
        user_id=user_id,
        question_id=question_id,
    )
    return BaseResponse(
        message="Deleted question successfully"
    )