from fastapi import APIRouter, Depends

from app.dto.common import BaseResponse
from app.dto.auth_dto import LoginRequest, LoginResponseData, LoginResponse, SignUpRequest, UserResponse
from app.services.account_services import AuthService
from app.helpers.auth_helpers import get_current_user

router = APIRouter(tags=['Auth'], prefix="/account")


@router.post(
    '/login',
    response_model=LoginResponse
)
async def user_login(
    data: LoginRequest
):
    access_token = await AuthService.login(
        email=data.email, 
        password=data.password
    )
    return LoginResponse(
        message='Logged in',
        data=LoginResponseData(access_token=access_token)
    )


@router.post(
    '/signup',
    response_model=BaseResponse
)
async def user_signup(
    data: SignUpRequest
):
    AuthService.signup(
        user_name=data.user_name,
        email=data.email,
        password=data.password
    )
    return BaseResponse(
        message='Succeed',
        error_code=0
    )


@router.get(
    '/user',
    response_model=UserResponse
)
async def get_current_user(
    user_id: str = Depends(get_current_user),
):
    user = AuthService.get_user_by_id(user_id)
    return UserResponse(
        message='Succeed',
        data=user
    )