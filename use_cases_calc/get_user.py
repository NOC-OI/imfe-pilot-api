"""
  GetUser Class: class for get data from Orcid.json file
"""
import json
import os
import time
from urllib.parse import unquote

import boto3
import jwt
import requests
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from jwt import DecodeError

load_dotenv()


class GetUser:
    """
    GetUser: class for get data from users

    This class has the following methods:
        * create_client: client  creation using boto3 for jasmin object store connection
        * signed_url: generate the signed url for the access control files
        * get_user: get user using code
        * get_token: get user by JWT token
    """

    def __init__(
        self,
        bucket: str = "haig-fras",
        base_url: str = None,
    ):
        """
        GetBucket class constructor. If you are planning to use parquet data, it
        is important to set some ENV variables related to object store.
        - JASMIN_API_URL
        - JASMIN_TOKEN
        - JASMIN_SECRET

        Args:
        bucket (str, optional): bucket name. Defaults to 'haig-fras'.
        base_url (_type_, optional): default bucket url. Defaults to
            None.
        """

        self.bucket = bucket

        if not base_url:
            base_url = os.environ.get("JASMIN_API_URL")

        self.base_url = f"{base_url}{self.bucket}/"
        self.client = None
        self.environment = os.environ.get("ENV")
        if self.environment == "DEV":
            self.user_login = "orcid_test.json"
        else:
            self.user_login = "orcid.json"

    def create_client(self):
        """
        create_client: client creation using boto3 for jasmin object store connection

        Args:
            ---

        Returns:
            A client for object store interaction
        """
        jasmin_api_url = os.environ.get("JASMIN_API_URL")
        jasmin_token = os.environ.get("JASMIN_TOKEN")
        jasmin_secret = os.environ.get("JASMIN_SECRET")
        jasmin_location = os.environ.get("JASMIN_LOCATION")

        if jasmin_location:
            client = boto3.client(
                region_name=jasmin_location,
                aws_access_key_id=jasmin_token,
                aws_secret_access_key=jasmin_secret,
                endpoint_url=jasmin_api_url,
                service_name="s3",
                verify=True,
            )
        else:
            client = boto3.client(
                aws_access_key_id=jasmin_token,
                aws_secret_access_key=jasmin_secret,
                endpoint_url=jasmin_api_url,
                service_name="s3",
                verify=True,
            )

        return client

    def signed_url(self, assets):
        """
        signed_url: generate the signed url for the access control files

        Args:
            ---

        Returns:
            A dict with the new signed urls
        """
        assets = json.loads(unquote(assets))

        expiration_time = 60 * 60  # Expiration time in seconds

        self.client = self.create_client()
        load_dotenv()
        key = os.getenv("HASH_TOKEN").encode("utf-8")
        fernet = Fernet(key)
        for layer_class in assets.keys():
            for layer_type in assets[layer_class].keys():
                signed_url = self.client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.bucket,
                        "Key": assets[layer_class][layer_type]["url"],
                    },
                    ExpiresIn=expiration_time,
                )
                assets[layer_class][layer_type]["signed_url"] = fernet.encrypt(
                    signed_url.encode()
                ).decode()

        return assets

    def get_user(self, code: str, state: str):
        """
        get_user: get user using code

        Args:
            code (str): a code string sent by login auth API
            state (str): a state that indicates the login provider

        Returns:
            token: a JWT token that represents the name and orcid_id of the user
        """

        with open(self.user_login, encoding="utf-8") as user_file:
            user_list = json.load(user_file)

        if self.environment != "DEV":
            if state == "microsoft":
                client_id = os.getenv("VITE_365_CLIENT_ID")
                url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
                data = {
                    "client_id": client_id,
                    "client_secret": os.getenv("VITE_365_CLIENT_SECRET"),
                    "code": code,
                    "redirect_uri": os.getenv("VITE_365_REDIRECT_URI"),
                    "grant_type": "authorization_code",
                    "scope": "openid profile email",
                }
                access_token_response = requests.post(
                    url=url, data=data, timeout=10
                ).json()
                token = access_token_response.get("id_token")
                response = jwt.decode(
                    token,
                    algorithms=jwt.get_unverified_header(token)["alg"],
                    options={"verify_signature": False},
                )

                response["orcid"] = response["preferred_username"].lower()

            else:
                url = "https://orcid.org/oauth/token"
                params = {
                    "client_id": os.getenv("VITE_ORCID_CLIENT_ID"),
                    "client_secret": os.getenv("VITE_ORCID_CLIENT_SECRET"),
                    "code": code,
                    "grant_type": "authorization_code",
                }
                access_token_response = requests.post(
                    url=url,
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    timeout=10,
                )
                response = access_token_response.json()

        else:
            if code == "XXXX":
                response = {"name": code, "orcid": "0000-0000-0000-0000"}
            else:
                response = {"name": code, "orcid": "0000-0000-0000-0001"}

        user = {"name": response["name"], "orcid": response["orcid"], "access": 0}

        if user["orcid"] in user_list["orcid"]:
            user["access"] = 1
        token = jwt.encode(
            {
                "name": user["name"],
                "orcid": user["orcid"],
                "access": user["access"],
                "exp": round(time.time()) + 3600 * 24 * 30,
            },
            "haig-fras",
            algorithm="HS256",
        )

        return token

    def get_token(self, token: str):
        """
        get_token: get user by JWT token

        Args:
            token (str): a JWT token that represents the name, orcid_id and access_token
            of the test user

        Returns:
                user: user name and orcid id
        """
        with open(self.user_login, encoding="utf-8") as user_file:
            user_list = json.load(user_file)

        try:
            user = jwt.decode(jwt=token, key="haig-fras", algorithms=["HS256"])
        except DecodeError:
            return "error"

        if user["orcid"] not in user_list["orcid"]:
            return "error"
        return user
