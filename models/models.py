"""
  user model: class for accesing the user database
"""

import json
import os
import time

import jwt
import requests
from dotenv import load_dotenv

from db.db import db, metadata, sqlalchemy

load_dotenv()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("orcid", sqlalchemy.String),
    sqlalchemy.Column("access_token", sqlalchemy.String),
)


class User:
    """
    User Class: class for accesing the user database

    This class has the following methods:
        * get: get user by id
        * get_all: get all users in the database
        * get_token: get user by JWT token
        * create: user create function
        * create_test: function to create and add a test user to the database.
        Created for development purposes
    """

    @classmethod
    async def get(cls, id_user: int):
        """
        get: get user by id_user
        Args:
                id_user (int): id of the user in the database

        Returns:
                user: user base scheme
        """
        query = users.select().where(users.c.id == id_user)
        user = db.execute(query).all()
        return user

    @classmethod
    async def get_all(cls):
        """
        get_all: get all users in the database

        Returns:
                list of users: list of users base scheme
        """

        query = users.select().where(True)
        user = db.execute(query).all()

        return user

    @classmethod
    async def create(cls, code: str):
        """
        create: user create function

        Args:
            code (str): a code string sent by ORCID auth API

        Returns:
            token: a JWT token that represents the name, orcid_id and access_token
            of the user
        """
        with open("orcid.json", encoding="utf-8") as user_file:
            user_list = json.load(user_file)

        access_token_response = requests.post(
            url="https://orcid.org/oauth/token",
            params={
                "client_id": os.getenv("VITE_ORCID_CLIENT_ID"),
                "client_secret": os.getenv("VITE_ORCID_CLIENT_SECRET"),
                "code": code,
                "grant_type": "authorization_code",
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=10,
        )

        response = access_token_response.json()

        db_user = {
            "name": response["name"],
            "orcid": response["orcid"],
            "access_token": response["access_token"],
        }
        query = users.select().where(users.c.orcid == db_user["orcid"])
        user = db.execute(query).all()

        if len(user) == 0:
            query = users.insert().values(db_user)
            db.execute(query)
            query = users.select().where(users.c.orcid == db_user["orcid"])
            user = db.execute(query).all()
        user = user[0]
        if user.orcid not in user_list["orcid"]:
            return "error"

        token = jwt.encode(
            {
                "name": user.name,
                "orcid": user.orcid,
                "sub": user.id,
                "exp": round(time.time()) + 3600 * 24 * 30,
            },
            "haig-fras",
            algorithm="HS256",
        )

        return token

    @classmethod
    async def create_test(cls, test: str):
        """
        create_test: function to create and add a test user to the database.
        Created for development purposes

        Args:
            test (str): values for the new user columns

        Returns:
            token: a JWT token that represents the name, orcid_id and access_token
            of the test user
        """

        db_user = {
            "name": test,
            "orcid": test,
            "access_token": test,
        }
        query = users.select().filter(users.c.orcid == db_user["orcid"])
        user = db.execute(query).all()
        if len(user) == 0:
            query = users.insert().values(db_user)
            db.execute(query)
            query = users.select().where(users.c.orcid == db_user["orcid"])
            user = db.execute(query).all()
        user = user[0]

        token = jwt.encode(
            {
                "name": user.name,
                "orcid": user.orcid,
                "sub": user.id,
                "exp": round(time.time()) + 3600 * 24 * 30,
            },
            "haig-fras",
            algorithm="HS256",
        )

        return token

    @classmethod
    async def get_token(cls, token: str):
        """
        get_token: get user by JWT token

        Args:
            token (str): a JWT token that represents the name, orcid_id and access_token
            of the test user

        Returns:
                user: user base scheme
        """
        db_user = jwt.decode(jwt=token, key="haig-fras", algorithms=["HS256"])
        id_user = db_user["sub"]

        query = users.select().where(users.c.id == id_user)
        user = db.execute(query).all()
        return user
