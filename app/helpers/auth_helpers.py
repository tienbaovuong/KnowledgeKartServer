import os
import jwt
import time

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.helpers.exceptions import PermissionDeniedException


default_secret_key = os.getenv('JWT_SECRET_KEY')
default_algorithm = os.getenv('JWT_ALGORITHM')

def generate_token(
    payload=None, secret_key=default_secret_key,
    algorithm=default_algorithm,
):
    payload = payload or {}
    access_token = jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm
    )
    if isinstance(access_token, str):
        return access_token
    else :
        return access_token.decode('utf-8')

def decode_token(
    encoded_token, leeway=0, secret_key=default_secret_key,
    algorithm=default_algorithm
):
    try:
        data = jwt.decode(
            encoded_token, secret_key,
            algorithms=[algorithm], leeway=leeway
        )
        return data
    except jwt.ExpiredSignatureError:
        raise PermissionDeniedException(
            'Signature expired. Please log in again.'
        )
    except jwt.InvalidTokenError:
        raise PermissionDeniedException('Invalid token. Please log in again.')
    
def login(user_id: str):
    payload = {
        "sub": "admin",
        "id": user_id,
        "exp": round(time.time()) + 86400, # 1 hour expire
    }
    return generate_token(payload, default_secret_key)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    
def get_current_user(token: str= Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise PermissionDeniedException(
            'Signature expired. Please log in again.'
        )
    return user.get("sub")
