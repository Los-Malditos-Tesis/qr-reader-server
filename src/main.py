from fastapi import FastAPI
from src.route.qr_routes import router as qr_router

app = FastAPI()

app.include_router(qr_router)