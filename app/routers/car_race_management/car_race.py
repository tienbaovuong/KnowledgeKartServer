from fastapi import APIRouter, Depends, Query

from app.dto.common import BaseResponse
from app.dto.car_race_dto import CarRacePaginationResponseData, CarRacePaginationResponse, CarRaceResponse, CarRacePutRequest
from app.helpers.auth_helpers import get_current_user
from app.helpers.exceptions import BadRequestException
from app.services.car_race_services import CarRaceService

router = APIRouter(tags=['Car Race'], prefix='/car_race')


@router.get(
    '/list',
    response_model=CarRacePaginationResponse,
)
async def get_list_car_races(
    user_id: str = Depends(get_current_user),
    page: int = Query(1),
    limit: int = Query(10),
):
    items, total = await CarRaceService.list_car_races(
        user_id=user_id,
        page=page,
        limit=limit,
    )

    return CarRacePaginationResponse(
        message="Get list car race successfully",
        data=CarRacePaginationResponseData(
            items=items,
            total=total,
        )
    )


@router.get(
    '/{car_race_id}',
)
async def get_car_race_by_id(
    car_race_id: str,
    user_id: str = Depends(get_current_user),
):
    car_race = await CarRaceService.get_car_race_by_id(
        user_id=user_id,
        car_race_id=car_race_id,
    )

    return CarRaceResponse(
        message="Get car race successfully",
        data=car_race
    )


@router.post(
    '/create',
)
async def create_car_race(
    create_car_race_data: CarRacePutRequest,
    user_id: str = Depends(get_current_user),
):
    await CarRaceService.create(
        user_id=user_id,
        new_car_race=create_car_race_data.dict(),
    )
    
    return BaseResponse(
        message="Created car race successfully"
    )


@router.put(
    '/{car_race_id}',
)
async def update_car_race_by_id(
    car_race_id: str,
    update_car_race_data: CarRacePutRequest,
    user_id: str = Depends(get_current_user),
):
    updated_data = await CarRaceService.put(
        user_id=user_id,
        car_race_id=car_race_id,
        update_data=update_car_race_data.dict(),
    )
    return CarRaceResponse(
        message="Updated car race successfully",
        data=updated_data
    )


@router.delete(
    '/{car_race_id}',
)
async def delete_car_race_by_id(
    car_race_id: str,
    user_id: str = Depends(get_current_user),
):
    await CarRaceService.delete(
        user_id=user_id,
        car_race_id=car_race_id,
    )
    return BaseResponse(
        message="Deleted car race successfully"
    )