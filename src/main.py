import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

from src.api import jobs, webhooks
from src.core.config import settings
import aio_pika

# Setup a logger for more structured output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The lifespan context manager is the modern way to handle startup/shutdown events.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    Connects to MongoDB on startup and closes the connection on shutdown.
    """
    logger.info("Application startup...")
    
    # --- Startup ---
    try:
        settings.log()          
        app.state.db_client = AsyncIOMotorClient(settings.MONGO_URI)
        
        # Is this a correct way to do this?
        await app.state.db_client.admin.command('ping')      
        app.state.db = app.state.db_client[settings.MONGO_DB_NAME]
        logger.info("Successfully connected to MongoDB.")

        rabbitmq_connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        rabbitmq_channel = await rabbitmq_connection.channel()
        
        # It's a good practice for the producer to declare the queue
        # to ensure it exists before trying to send messages.
        # durable=True means the queue will survive a RabbitMQ restart.
        await rabbitmq_channel.declare_queue(
            settings.RABBITMQ_QUEUE_NAME, 
            durable=True
        )
        
        app.state.rabbitmq_connection = rabbitmq_connection
        app.state.rabbitmq_channel = rabbitmq_channel
        logger.info("Successfully connected to RabbitMQ.")
        
    except (ConnectionFailure, aio_pika.exceptions.AMQPConnectionError) as e:
        logger.critical(f"Could not connect to required services: {e}")
        raise # re-raise
        
    yield # The application runs here
    
    # --- Shutdown ---
    logger.info("Application shutdown...")
    if hasattr(app.state, 'rabbitmq_connection'):
        await app.state.rabbitmq_connection.close()
        logger.info("RabbitMQ connection closed.")

    if hasattr(app.state, 'db_client'):
        app.state.db_client.close()
        logger.info("MongoDB connection closed.")


app = FastAPI(
    title="Async Job Processor API",
    description="An API to handle long-running background jobs.",
    version="1.0.0",
    lifespan=lifespan  # Register the lifespan event handler
)

# Health check
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Welcome to the Job Processor API!"}

# Include the routers from the other files
app.include_router(jobs.router)
app.include_router(webhooks.router)
