from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_filename: str = 'specimen_app.db'


settings = Settings()
