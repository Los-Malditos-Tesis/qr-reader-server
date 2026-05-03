from fastapi import APIRouter, File, UploadFile, Form
import numpy as np
import cv2
import json

from src.service.qr_service import process_qr
from src.log.logger import logger

router = APIRouter()


@router.post("/read-qr/")
async def read_qr_endpoint(
    file: UploadFile = File(...),
    boxes: str = Form(...)
):
    try:
        contents = await file.read()

        logger.info("[START] read_qr_endpoint called")

        npimg = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image received")

        logger.info(f"[IMAGE] shape={image.shape}")

        boxes = json.loads(boxes)
        logger.info(f"[BOXES] count={len(boxes.get('boxes', []))}")

        results = process_qr(image, boxes)

        logger.info("[END] read_qr_endpoint finished successfully")

        return {
            "success": True,
            "results": results
        }

    except Exception as e:
        logger.error(f"[ERROR] error reading QR code: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }