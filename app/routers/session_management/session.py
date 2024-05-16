import json
import asyncio
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query

from app.dto.common import BaseResponse
from app.helpers.auth_helpers import get_current_user
from app.services.live_session_services import LiveSessionService
from app.helpers.exceptions import BadRequestException
from app.database import pub, psub

router = APIRouter(tags=["Car Race Live Session"], prefix="/session")


@router.put(
    "/start/{session_id}",
)
async def start_session_by_id(
    session_id: str,
    user_id: str = Depends(get_current_user),
):
    await LiveSessionService.start(
        user_id=user_id,
        session_id=session_id,
    )
    return BaseResponse(
        message="Started session successfully",
    )


@router.put(
    "/end/{session_id}",
)
async def end_session_by_id(
    session_id: str,
    user_id: str = Depends(get_current_user),
):
    await LiveSessionService.end(
        user_id=user_id,
        session_id=session_id,
    )
    return BaseResponse(
        message="Ended session successfully",
    )


@router.websocket("/ws_user/{session_id}")
async def user_session_connect(websocket: WebSocket, session_id: str):
    await websocket.accept()
    temp_session = await LiveSessionService.get_temp_session(session_id)
    if not temp_session:
        statis_session = await LiveSessionService.get_statis_session(session_id)
        await websocket.send_json(statis_session.dict())
        await websocket.close()
    await websocket.send_text(json.dumps(temp_session))
    async with psub as p:
        await p.subscribe(f"channel:{session_id}")
        if p != None:
            while True:
                # Get message from redis channel
                message = await p.get_message(
                    ignore_subscribe_messages=True, timeout=0.5
                )
                await asyncio.sleep(1)
                if message != None:
                    data = json.loads(message["data"])
                    topic = data["topic"]
                    value = data["value"]
                    if topic in [
                        "update_status",
                        "client_update_users",
                        "client_update_result",
                    ]:
                        await websocket.send_text(
                            json.dumps({"event": topic, "value": value})
                        )
                    if topic == "update_status" and value == "ENDED":
                        await websocket.close()


@router.websocket("/ws_guest/{session_id}/{client_id}")
async def session_connect(websocket: WebSocket, session_id: str, client_id: str):
    await websocket.accept()
    if not client_id:
        raise BadRequestException("Missing client id")
    temp_session = await LiveSessionService.get_temp_session(session_id)
    if not temp_session:
        statis_session = await LiveSessionService.get_statis_session(session_id)
        await websocket.send_json(statis_session.dict())
        await websocket.close()
    await websocket.send_json(temp_session)
    try:
        # Init message with user (uid, name, point, time) and send back current results
        first_message = await websocket.receive_json()
        await pub.publish(
            f"channel:{session_id}",
            json.dumps({"topic": "client_join", "value": first_message}),
        )
        done, pending = await asyncio.wait(
            [
                get_user_action(websocket, session_id),
                send_user_update(websocket),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        await websocket.close()
        await pub.publish(
            f"channel:{session_id}",
            json.dumps({"topic": "client_leave", "value": client_id}),
        )
    except WebSocketDisconnect:
        await pub.publish(
            f"channel:{session_id}",
            json.dumps({"topic": "client_leave", "value": client_id}),
        )


# Assist function
async def get_user_action(websocket: WebSocket, session_id: str):
    while True:
        message = await websocket.receive_json()
        await pub.publish(
            f"channel:{session_id}",
            json.dumps({"topic": "client_update", "value": message}),
        )


async def send_user_update(websocket: WebSocket):
    async with psub as p:
        while True:
            # Get message from redis channel
            message = await p.get_message(ignore_subscribe_messages=True, timeout=0.5)
            await asyncio.sleep(0)
            if message != None:
                data = json.loads(message["data"])
                topic = data["topic"]
                value = data["value"]
                if topic in [
                    "update_status",
                    "client_update_users",
                    "client_update_result",
                ]:
                    await websocket.send_text(
                        json.dumps({"event": topic, "value": value})
                    )
                if topic == "update_status" and value == "ENDED":
                    await websocket.close()
