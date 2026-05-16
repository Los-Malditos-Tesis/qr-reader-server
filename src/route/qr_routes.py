from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
import numpy as np
import cv2

from src.service.qr_service import read_multiple_qr
from src.log.logger import logger
from src.client.mqtt_client import mqtt_manager
from src.config.setting import settings

router = APIRouter()


@router.post("/read-qr/")
async def read_qr_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    correlationId: str = Form(...),
    cameraCode: str = Form(...)
):

    try:
        contents = await file.read()

        npimg = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if image is None:
            return {"success": False, "error": "Invalid image"}

        results = read_multiple_qr(image)

        payload = {
            "correlationId": correlationId,
            "cameraCode": cameraCode,
            "results": results,
            "found": len(results) > 0
        }

        # MQTT ASÍNCRONO (NO bloquea request)
        background_tasks.add_task(
            mqtt_manager.publish,
            settings.MQTT_TOPIC_RESULT,
            payload
        )

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