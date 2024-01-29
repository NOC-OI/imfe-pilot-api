"""
  db: general connection to the DB.
"""

import os

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()
# db = Database(os.getenv("DATABASE_URL"))
metadata = sqlalchemy.MetaData()
