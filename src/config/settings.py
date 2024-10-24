import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):

    # postgres related settings
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB = os.getenv('POSTGRES_DB')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')


settings = Settings()
