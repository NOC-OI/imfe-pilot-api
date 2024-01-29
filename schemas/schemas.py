# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods
"""
    Schema for user creation, migration and select
"""
from pydantic import BaseModel


class User(BaseModel):
    """
    User: user Schema Model

    Args:
        BaseModel (BaseModel): User Base Model
    """

    name: str
    orcid: str
    access_token: str

    class Config:
        """
        config: class for define that you will need to access data base
        """

        orm_mode = True
