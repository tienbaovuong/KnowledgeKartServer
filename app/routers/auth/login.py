from app.dto.common import BaseResponse
from app.dto.auth_dto import LoginRequest, LoginResponseData, LoginResponse, SignUpRequest
from fastapi import APIRouter
from app.helpers.auth_helpers import login

router = APIRouter(tags=['Auth'])


@router.post(
    '/login',
    response_model=LoginResponse
)
async def user_login(
    data: LoginRequest
):
    user_id = data.email
    access_token = login(user_id)
    return LoginResponse(
        message='Loged in',
        data=LoginResponseData(access_token=access_token)
    )


@router.post(
    '/signup',
    response_model=BaseResponse
)
async def user_signup(
    data: SignUpRequest
):
    # TODO: Implement user signup logic
    # - Validate signup request
    return BaseResponse(
        message='User created successfully',
        error_code=0
    )