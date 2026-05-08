from fastapi import APIRouter, File, UploadFile, Form
import numpy as np
import cv2
import json

from src.service.qr_service import read_multiple_qr
from src.log.logger import logger

router = APIRouter()


@router.post("/read-qr/")
async def read_qr_endpoint(
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()

        npimg = np.frombuffer(contents, np.uint8)

        image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image")

        results = read_multiple_qr(image)

        return {
            "success": True,
            "results": results
        }

    except Exception as e:
        logger.error(str(e))

        return {
            "success": False,
            "error": str(e)
        }