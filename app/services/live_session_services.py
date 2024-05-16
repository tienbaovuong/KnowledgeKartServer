import logging
import json
import asyncio
from queue import Queue
from datetime import datetime
from beanie import PydanticObjectId

from app.database import psub, pub, redis
from app.models.car_race_session import CarRaceSession, SessionStatus
from app.models.car_race import CarRace
from app.models.question import Question
from app.dto.question_dto import QuestionPutRequest
from app.dto.session_dto import SessionFullResponseData
from app.helpers.exceptions import NotFoundException

_logger = logging.getLogger(__name__)


class LiveSessionService:

    @staticmethod
    async def get_temp_session(session_id: str):
        # Gather questions, settings, session status, list player, player data and ranking
        status = await pub.hget(f"settings:{session_id}", "status")
        if not status or status == "ENDED":
            return None
        settings, questions, client_list, client_data, ranking = await asyncio.gather(
            pub.hgetall(f"settings:{session_id}"),
            pub.get(f"questions:{session_id}"),
            pub.smembers(f"current_clients:{session_id}"),
            pub.hgetall(f"results:{session_id}"),
            pub.get(f"ranking:{session_id}"),
        )
        if not ranking:
            ranking = "[]"
        for key, value in client_data.items():
            client_data[key] = json.loads(value)
        session = {
            "session_status": settings["status"],
            "bonus": settings["bonus"],
            "penalty": settings["penalty"],
            "session_name": settings["session_name"],
            "questions": json.loads(questions),
            "client_list": list(client_list),
            "client_data": client_data,
            "ranking": json.loads(ranking),
        }
        return session

    @staticmethod
    async def get_statis_session(session_id: str) -> dict:
        query = CarRaceSession.find_one({"_id": PydanticObjectId(session_id)})
        session = await query.project(SessionFullResponseData)
        if not session:
            raise NotFoundException("Session not found")
        return_data = session.dict(
            exclude={"id", "_id", "car_race_id", "created_at", "updated_at"}
        )
        return return_data

    @staticmethod
    async def start(user_id: str, session_id: str):
        session = await CarRaceSession.find_one(
            {"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(session_id)}
        )
        if not session:
            raise NotFoundException("Session not found")
        update_data = {
            "session_status": SessionStatus.STARTED,
            "updated_at": datetime.now(),
        }
        await session.update({"$set": update_data})
        await redis.hset(f"settings:{session_id}", "status", "STARTED")
        await pub.publish(
            f"channel:{session_id}",
            json.dumps({"topic": "update_status", "value": "STARTED"}),
        )

    @staticmethod
    async def end(user_id: str, session_id: str):
        session = await CarRaceSession.find_one(
            {"user_id": PydanticObjectId(user_id), "_id": PydanticObjectId(session_id)}
        )
        if not session:
            raise NotFoundException("Session not found")
        update_data = {
            "session_status": SessionStatus.ENDED,
            "updated_at": datetime.now(),
        }
        await session.update({"$set": update_data})
        await redis.hset(f"settings:{session_id}", "status", "ENDED")
        await pub.publish(
            f"channel:{session_id}",
            json.dumps({"topic": "update_status", "value": "ENDED"}),
        )


async def start_session_in_background(session_id: str, start_time: datetime):
    # Gather resources
    session = await CarRaceSession.find_one({"_id": PydanticObjectId(session_id)})
    race_id = session.car_race_id
    car_race = await CarRace.find_one({"_id": PydanticObjectId(race_id)})
    library_id = car_race.library_id
    question_list = (
        await Question.find({"library_id": PydanticObjectId(library_id)})
        .project(QuestionPutRequest)
        .to_list()
    )
    parsed_question_list = []
    for question in question_list:
        parsed_question_list.append(question.dict())
    async with psub as p:
        # Subcribe to session redis channel
        await p.subscribe(f"channel:{session_id}")
        if p != None:
            # On create session
            loop_time = datetime.now()
            status = "CREATED"
            message_queue = Queue()
            await redis.set(f"questions:{session_id}", json.dumps(parsed_question_list))
            await redis.hset(
                f"settings:{session_id}",
                mapping={
                    "status": "CREATED",
                    "bonus": car_race.bonus_time_setting,
                    "penalty": car_race.penalty_time_setting,
                    "session_name": session.car_race_session_name,
                },
            )
            while True:
                # Loop to get published message from redis
                total_delta = datetime.now() - start_time
                if total_delta.total_seconds() > 15 * 60 and status == "CREATED":
                    # End session if stayed in CREATED for over 15 minutes
                    await pub.publish(
                        f"channel:{session_id}",
                        json.dumps({"topic": "update_status", "value": "ENDED"}),
                    )
                    update_data = {
                        "session_status": SessionStatus.ENDED,
                        "updated_at": datetime.now(),
                    }
                    await session.update({"$set": update_data})
                    await redis.hset(f"settings:{session_id}", "status", "ENDED")
                    await pub.publish(
                                f"channel:{session_id}",
                                json.dumps(
                                    {
                                        "topic": "close_websocket",
                                        "value": ""
                                    }
                                ),
                            )
                    break

                if total_delta.total_seconds() > 60 * 60 and status == "STARTED":
                    # End session if total time over 15 minutes
                    await pub.publish(
                        f"channel:{session_id}",
                        json.dumps({"topic": "update_status", "value": "ENDED"}),
                    )
                    update_data = {
                        "session_status": SessionStatus.ENDED,
                        "updated_at": datetime.now(),
                    }
                    await session.update({"$set": update_data})
                    await redis.hset(f"settings:{session_id}", "status", "ENDED")
                    await pub.publish(
                                f"channel:{session_id}",
                                json.dumps(
                                    {
                                        "topic": "close_websocket",
                                        "value": ""
                                    }
                                ),
                            )
                    break
                # Get message from redis channel
                message = await p.get_message(
                    ignore_subscribe_messages=True, timeout=0.5
                )
                print(message)
                if message != None:
                    data = json.loads(message["data"])
                    topic = data["topic"]
                    value = data["value"]
                    if topic == "update_status":
                        status = value
                        if value == "ENDED":
                            # Update temp result from redis to MongoDB when session ended
                            update_result = await pub.hgetall(f"results:{session_id}")
                            ranking = await pub.get(f"ranking:{session_id}")
                            if not ranking:
                                ranking = "[]"
                            for key, value in update_result.items():
                                update_result[key] = json.loads(value)
                            update_data = {
                                "result": {
                                    "results": update_result,
                                    "ranking": json.loads(ranking),
                                },
                                "updated_at": datetime.now(),
                            }
                            await update_result_to_client(
                                session_id, json.loads(ranking), update_result
                            )
                            await session.update({"$set": update_data})
                            await pub.publish(
                                f"channel:{session_id}",
                                json.dumps(
                                    {
                                        "topic": "close_websocket",
                                        "value": ""
                                    }
                                ),
                            )
                            break
                    elif topic == "client_update":
                        # Gather player action in a certain amount of time (1 second)
                        message_queue.put(data["value"])
                    elif topic == "client_join":
                        # Logic when someone joins the session
                        await redis.sadd(f"current_clients:{session_id}", value["uid"])
                        await redis.hset(
                            f"results:{session_id}", value["uid"], json.dumps(value)
                        )
                        await update_current_clients(session_id)
                    elif topic == "client_leave":
                        # Logic when someone leaves the session
                        await redis.srem(f"current_clients:{session_id}", value)
                        await update_current_clients(session_id)

                delta = datetime.now() - loop_time
                qSize = message_queue.qsize()
                if delta.total_seconds() >= 1 and qSize:
                    loop_time = datetime.now()
                    # Logic for player actions (batch)
                    old_results: dict = await pub.hgetall(f"results:{session_id}")
                    while message_queue.qsize():
                        # Player action data structure {uid, name, point, time}
                        new_update = message_queue.get()
                        uid = new_update["uid"]
                        old_results[uid] = json.dumps(new_update)
                    # sort new results
                    if qSize:
                        try:
                            await redis.hset(
                                f"results:{session_id}", mapping={**old_results}
                            )
                            ranking = []
                            score_list = list(old_results.values())
                            for index, score in enumerate(score_list):
                                score_list[index] = json.loads(score)
                            sorted_score_list = sorted(
                                score_list, key=lambda x: (-x["point"], x["time"])
                            )
                            for score in sorted_score_list:
                                ranking.append(score["uid"])
                            await redis.set(
                                f"ranking:{session_id}", json.dumps(ranking)
                            )
                            for key, value in old_results.items():
                                old_results[key] = json.loads(value)
                            await update_result_to_client(
                                session_id, ranking, old_results
                            )
                        except Exception as e:
                            e.with_traceback()
                            print(e)


async def update_current_clients(session_id: str):
    client_lists, client_data = await asyncio.gather(
        pub.smembers(f"current_clients:{session_id}"),
        pub.hgetall(f"results:{session_id}"),
    )
    for key, value in client_data.items():
        client_data[key] = json.loads(value)
    await pub.publish(
        f"channel:{session_id}",
        json.dumps(
            {
                "topic": "client_update_users",
                "value": {
                    "player_list": list(client_lists),
                    "data": client_data,
                },
            }
        ),
    )


async def update_result_to_client(session_id: str, ranking: list, client_data: dict):
    await pub.publish(
        f"channel:{session_id}",
        json.dumps(
            {
                "topic": "client_update_result",
                "value": {
                    "ranking": ranking,
                    "data": client_data,
                },
            }
        ),
    )
