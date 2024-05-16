import json
from pathlib import Path
from typing import Type, Union
from beanie import init_beanie, Document
from motor import motor_asyncio

from app.settings.app_settings import AppSettings
from app.models.user_account import UserAccount
from app.models.library import Library
from app.models.question import Question
from app.models.car_race import CarRace
from app.models.car_race_session import CarRaceSession
import logging

_logger = logging.getLogger(__name__)


async def init_collection(col: Type[Document], file_path: Union[str, Path]):
    existing_items = await col.find_all(limit=5).to_list()
    if not existing_items:
        f = open(file_path, encoding="utf-8")
        default_items = json.load(f)
        f.close()
        for default_item in default_items:
            item_id = default_item.get("_id")
            if item_id and item_id.get("$oid"):
                default_item.update({"_id": item_id.get("$oid")})
            item_created_at = default_item.get("created_at")
            if item_created_at and item_created_at.get("$date") and item_created_at.get("$date").get("$numberLong"):
                default_item.update({"created_at": item_created_at.get("$date").get("$numberLong")})
            item_updated_at = default_item.get("updated_at")
            if item_updated_at and item_updated_at.get("$date") and item_updated_at.get("$date").get("$numberLong"):
                default_item.update({"updated_at": item_updated_at.get("$date").get("$numberLong")})
            item = col(**default_item)
            await item.create()
        _logger.info(f"Successfully init data for collection {col.__name__}")


# async def init_collections():
#     # Data collections
#     await init_collection(
#         UserAccount,
#         Path(__file__).parent.resolve() / "data/thesis_data.json",
#     )


async def initialize():
    app_settings = AppSettings()

    # CREATE MOTOR CLIENT
    client = motor_asyncio.AsyncIOMotorClient(app_settings.mongo_dsn, maxPoolSize=5)

    # INIT BEANIE
    await init_beanie(
        client.get_database(),
        document_models=[
            UserAccount,
            Library,
            Question,
            CarRace,
            CarRaceSession
        ],
    )

    # CREATE DATA
    # await init_collections()

    _logger.info("Database is successfully initialized.")