import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # mongoDB stuff
    MONGO_URI: str
    MONGO_DB_NAME: str 
    MONGO_COLLECTION_NAME: str

    # RabbitMQ stuff
    RABBITMQ_URL: str
    RABBITMQ_QUEUE_NAME: str 

    # Pydantic settings config
    model_config = SettingsConfigDict(
        env_file=".env",
    )
    
    def log(self):
        """
        Logs essential, non-sensitive information about the loaded settings.
        """
        
        logger.info("--- Application Settings Loaded ---")
        logger.info(f"MONGO_URI: <redacted> (Length: {len(self.MONGO_URI)})")
        logger.info(f"MONGO_DB_NAME: {self.MONGO_DB_NAME}")
        logger.info(f"MONGO_COLLECTION_NAME: {self.MONGO_COLLECTION_NAME}")
        logger.info(f"RABBITMQ_URL: <redacted> (Length: {len(self.RABBITMQ_URL)})")
        logger.info(f"RABBITMQ_QUEUE_NAME: {self.RABBITMQ_QUEUE_NAME}")
        logger.info("-----------------------------------")


# Create a single, validated instance of the settings
try:
    settings = Settings()
except Exception as e:
    # This provides the primary safety net. If a required env var is missing,
    # Pydantic will raise a validation error and the app won't start.
    # If we used spring boot here, these things sort of come out of the box.
    logger.critical(f"Failed to load settings. Missing environment variables?")
    # Re-raising is crucial to stop the application from starting in a broken state.
    raise