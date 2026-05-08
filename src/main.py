from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.route.qr_routes import router as qr_router
from src.client.mqtt_client import mqtt_manager
from src.log.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("[APP] Starting MQTT connection...")
        mqtt_manager.connect()

        yield

    finally:
        logger.info("[APP] Shutting down MQTT...")
        mqtt_manager.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(qr_router)