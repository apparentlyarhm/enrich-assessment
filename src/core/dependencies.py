import aio_pika
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase

def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db

def get_rabbitmq_channel(request: Request) -> aio_pika.Channel:
    return request.app.state.rabbitmq_channel