from app.models.base import RootModel, RootEnum

class ClusterHistory(RootModel):
    class Collection:
        name = "user_account"

    user_name: str
    email: str
    #hash password before put in db / best do it from FE
    password: str