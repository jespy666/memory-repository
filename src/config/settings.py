import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):

    # postgres related settings
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    POSTGRES_PORT: int = os.getenv('POSTGRES_PORT')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST')

    # JWT related settings
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = os.getenv('ALGORITHM')
    ACTIVATE_TOKEN_EXPIRE_MINUTES: int = os.getenv('ACTIVATE_TOKEN_EXPIRE_MINUTES')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    REFRESH_TOKEN_EXPIRE_MINUTES: int = os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')  # noqa: E501

    # SMTP related settings
    SMTP_HOST: str = os.getenv('SMTP_HOST')
    SMTP_USER: str = os.getenv('SMTP_USER')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD')
    SMTP_PORT: int = os.getenv('SMTP_PORT')

    def get_connection_string(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
