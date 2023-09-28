from os import getenv
from dotenv import load_dotenv, find_dotenv

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())
PG_USER = getenv("PG_USER")
PG_PASSWORD = getenv("PG_PASSWORD")
PG_DB = getenv("PG_DB")
PG_HOST = getenv("PG_HOST")
PG_PORT = getenv("PG_PORT")

PG_DSN = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_async_engine(PG_DSN)
Session = sessionmaker(class_=AsyncSession, expire_on_commit=False, bind=engine)

Base = declarative_base()


class SwapiPeople(Base):
    __tablename__ = "swapi_people"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    birth_year = Column(String)
    eye_color = Column(String)
    films = Column(JSON)
    gender = Column(String)
    hair_color = Column(String)
    height = Column(String)
    homeworld = Column(String)
    mass = Column(String)
    skin_color = Column(String)
    created = Column(String)
    edited = Column(String)
    species = Column(JSON)
    starships = Column(JSON)
    url = Column(String)
    vehicles = Column(JSON)
