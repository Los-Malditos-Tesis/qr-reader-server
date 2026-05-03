from fastapi import FastAPI
from src.route.qr_routes import router as qr_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(qr_router)