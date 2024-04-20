from app.dto.auth_dto import LoginRequest,LoginResponseData, LoginResponse
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
    access_token = login(username=data.username, password=data.password)
    return LoginResponse(
        message='Loged in',
        data=LoginResponseData(access_token=access_token)
    )