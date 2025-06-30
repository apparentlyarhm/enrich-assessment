from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URI: str = "hmm"
    MONGO_DB_NAME: str = "job_processor_db"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()