from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from src.api import jobs, webhooks
from src.core.config import settings

# The lifespan context manager is the modern way to handle startup/shutdown events.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Create the MongoDB client
    app.state.db_client = AsyncIOMotorClient(settings.MONGO_URI)
    # Get the database object. We can now access this from our endpoints.
    app.state.db = app.state.db_client[settings.MONGO_DB_NAME]
    print("Successfully connected to MongoDB.")
    
    yield # The application runs here
    
    # --- Shutdown ---
    app.state.db_client.close()
    print("MongoDB connection closed.")


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
