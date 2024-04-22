from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel

class UserAccount(RootModel):
    class Collection:
        name = "user_account"
        indexes = [
            IndexModel(
                [
                    ("email", ASCENDING),
                ],
                unique=True,
            )
        ]

    user_name: str
    email: str
    #hash password before put in db / best do it from FE
    password: str