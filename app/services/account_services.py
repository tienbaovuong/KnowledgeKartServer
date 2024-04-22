import logging
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.models.user_account import UserAccount
from app.dto.auth_dto import UserResponseData
from app.helpers.exceptions import NotFoundException, BadRequestException
from app.helpers.auth_helpers import login_token

_logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    async def login(email: str, password: str) -> UserAccount:
        user = await UserAccount.find_one(UserAccount.email == email)
        if not user:
            raise NotFoundException("Wrong email or password")
        if user.password != password:
            raise NotFoundException("Wrong email or password")
        access_token = login_token(str(user.id))
        _logger.info(f"User logged in: {user.user_name}")
        return access_token
    
    @staticmethod
    async def signup(user_name: str, email: str, password: str) -> UserAccount:
        new_user = UserAccount(
            user_name=user_name,
            email=email,
            password=password
        )
        try:
            await new_user.save()
        except DuplicateKeyError:
            raise BadRequestException("Email already registered")
        _logger.info(f"New user created: {new_user.user_name}")
        return new_user
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> UserResponseData:
        user = await UserAccount.find_one(UserAccount.id == PydanticObjectId(user_id)).project(UserResponseData)
        if not user:
            raise NotFoundException(f"User not found")
        return user