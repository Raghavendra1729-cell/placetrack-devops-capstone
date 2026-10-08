from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://placetrack:placetrack@localhost:5432/placetrack"


settings = Settings()
