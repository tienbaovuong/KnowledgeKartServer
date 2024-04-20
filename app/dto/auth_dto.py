from app.dto.common import BaseResponseData
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str

class SignUpRequest(BaseModel):
    user_name: str
    password: str
    email: str

class LoginResponseData(BaseModel):
    access_token: str

class LoginResponse(BaseResponseData):
    data: LoginResponseData