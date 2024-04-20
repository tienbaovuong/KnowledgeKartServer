from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.helpers.exceptions import (
    BadRequestException, NotFoundException, 
    PermissionDeniedException, ConflictException
)

from app.dto.common import BaseResponse
import logging

_logger = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(ValueError)
    async def handle_user_value_error(
        request: Request,
        exc: ValueError
    ):
        error_message = str(exc) or 'Value Error'
        _logger.warning(f'ValueError {error_message}')
        return JSONResponse(
            status_code=422,
            content=BaseResponse(
                error_code=-1,
                message=str(exc)).dict()
        )

    @app.exception_handler(RequestValidationError)
    async def request_validator_handler(
        request: Request,
        exc: RequestValidationError
    ):
        error_message = str(exc) or 'RequestValidationError'
        _logger.warning(f'RequestValidationError {error_message}')
        return JSONResponse(status_code=422, content={'error': error_message})

    @app.exception_handler(BadRequestException)
    async def bad_request_handler(
        request: Request,
        exc: BadRequestException
    ):
        error_message = str(exc) or 'Bad Request'
        _logger.warning(f'BadRequestException {error_message}')
        return JSONResponse(status_code=400, content={'error': error_message})

    @app.exception_handler(PermissionDeniedException)
    async def permission_denied_handler(
        request: Request,
        exc: PermissionDeniedException
    ):
        error_message = str(exc) or 'Permission Denied'
        _logger.warning(f'PermissionDeniedException {error_message}')
        return JSONResponse(status_code=401, content={'error': error_message})

    @app.exception_handler(NotFoundException)
    async def not_found_handler(
        request: Request,
        exc: NotFoundException
    ):
        error_message = str(exc) or 'Not Found'
        _logger.warning(f'NotFoundException {error_message}')
        return JSONResponse(status_code=404, content={'error': error_message})

    @app.exception_handler(ConflictException)
    async def conflict_handler(
        request: Request,
        exc: ConflictException
    ):
        error_message = str(exc) or 'Conflict'
        _logger.warning(f'ConflictException {error_message}')
        return JSONResponse(status_code=469, content={'error': error_message})