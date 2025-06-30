import logging
from urllib.parse import urlparse, urlunparse
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str = "job_processor_db"

    # Pydantic settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8' 
    )
    
    def __init__(self):
        """
        Logs essential, non-sensitive information about the loaded settings.
        """
        # Never log the full MONGO_URI. We will parse it and mask the password.
        try:
            parsed_uri = urlparse(self.MONGO_URI)
            masked_netloc = f"{parsed_uri.username}:***@{parsed_uri.hostname}"
            if parsed_uri.port:
                masked_netloc += f":{parsed_uri.port}"
            
            masked_uri = urlunparse(parsed_uri._replace(netloc=masked_netloc))
        except Exception:
            masked_uri = "Could not parse URI for masking."
        
        logger.info("--- Application Settings Loaded ---")
        logger.info(f"MONGO_URI: {masked_uri} (Length: {len(self.MONGO_URI)})")
        logger.info(f"MONGO_DB_NAME: {self.MONGO_DB_NAME}")
        logger.info("-----------------------------------")


# Create a single, validated instance of the settings
try:
    settings = Settings()
except Exception as e:
    # This provides the primary safety net. If a required env var is missing,
    # Pydantic will raise a validation error and the app won't start.
    logger.critical(f"Failed to load settings. Missing environment variables?")
    # Re-raising is crucial to stop the application from starting in a broken state.
    raise