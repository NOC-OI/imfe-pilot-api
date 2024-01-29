"""
Router module for user entrypoints.

This router contains the following functions:
    * get_user: get all users on the database
    * get_signed_url_by_token: get signed url for filenames using user jwt token.
    If the user is on the database, it will access JASMIN Object Store to generate
    the signed urls
    * get_user_by_id: get user by id on the database
    * create_user: create user function, that access ORCID API and save a new user
    at the database
    * create_user_test: function to create and add a test user to the database.
    Created for development purposes
"""
import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from use_cases_calc.get_user import GetUser

# from models.models import User as ModelUser
# from schemas.schemas import User as SchemaUser
# from use_cases_calc.get_bucket import GetBucket

load_dotenv()

router = APIRouter()


# @router.get("/")
# async def get_user():
#     """
#     get_user: get all users on the database

#     Returns:
#         List[UserModel]: a list of all the user that are saved on the database
#     """
#     user = await ModelUser.get_all()
#     return user


@router.get("/aws")
def get_signed_url_by_token(token: str, assets: str = None, base_url: str = None):
    """
    get_signed_url_by_token: get signed url for filenames using user jwt token.
    If the user is on the database, it will access JASMIN Object Store to generate
    the signed urls

    Args:
        token (str): jwt token
        assets (str): the assets that will be converted
        base_url (str): base url of the object store

    Returns:
        filenames: a dictionary of the filenames with signed_url key included
    """
    filenames = ""
    if not base_url:
        base_url = os.environ.get("JASMIN_API_URL")

    orcid = GetUser(bucket="haig-fras-private", base_url=base_url)
    user = orcid.get_token(token)

    if user and user != "error":
        filenames = orcid.signed_url(assets)

    return filenames


# @router.get("/{id_user}", response_model=SchemaUser)
# async def get_user_by_id(id_user: int):
#     """
#     get_user_by_id: get user by id on the database

#     Args:
#         id_user (int): id of the user on the database

#     Returns:
#         UserModel: a user with the defined id

#     """
#     user = await ModelUser.get(id_user)
#     return SchemaUser(**user).dict()


@router.post("/")
def create_user(code: str, state: str):
    """
    create_user: create user function, that access ORCID API and save a new user
    at the database

    Args:
        code (str): a code string sent by login auth API
        state (str): a state that indicates the login provider

    Raises:
        HTTPException: if you pass a wrong user code, like error, it will return
        a code 404 response and a error message

    Returns:
        UserModel: a user related to the code
    """
    # user = await ModelUser.create(code)

    get_user = GetUser()
    user = get_user.get_user(code, state)

    if user == "error":
        raise HTTPException(status_code=404, detail="User not allowed")
    return user


# @router.post("/create_test")
# async def create_user_test(test: str = "test"):
#     """
#     create_user_test: function to create and add a test user to the database.
#     Created for development purposes

#     Args:
#         test (str): values for the new user columns

#     Returns:
#         UserModel: a user related to the test argument
#     """
#     user = await ModelUser.create_test(test)
#     return user
