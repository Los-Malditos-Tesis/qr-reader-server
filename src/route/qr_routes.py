from fastapi import APIRouter, File, UploadFile, Form
import numpy as np
import cv2
import json

from src.service.qr_service import process_qr

router = APIRouter()


@router.post("/read-qr/")
async def read_qr_endpoint(
    file: UploadFile = File(...),
    boxes: str = Form(...)
):
    contents = await file.read()

    npimg = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    boxes = json.loads(boxes)

    results = process_qr(image, boxes)

    return {
        "success": True,
        "results": results
    }