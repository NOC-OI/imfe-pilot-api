"""
FastAPI module that represent the root of the API

This module imports the following routes and endpoints:

This module contains the following functions:
    * docs: Open the documentation of the API
    * test: A simple test that the API is working.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import calc, data, user

# app = FastAPI(title="Haig Fras Digital Twin API", docs_url=None)
app = FastAPI(title="Haig Fras Digital Twin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    allow_credentials=True,
)


# @app.get("/")
# def docs():
#     """
#     docs: Open the documentation of the API

#     Returns:
#         RedirectResponse: redirect your response to the API Documentation
#     """
#     return RedirectResponse(url="/docs/")


@app.get("/")
def test():
    """
    test: A simple test that the API is working.

    Returns:
        dict: a dictionary with the information that the API si working
    """

    return {"API": "I'm alive"}


#######################
# V1
#######################
app.include_router(user.router, prefix="/v1/user", tags=["user"])
app.include_router(data.router, prefix="/v1/data", tags=["data"])
app.include_router(calc.router, prefix="/v1/calc", tags=["calc"])
