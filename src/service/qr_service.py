import cv2
import time
from src.log.logger import logger

# Detector global (reutilizable)
detector = cv2.QRCodeDetector()


def read_qr_opencv(image):
    try:
        logger.info("[DETECT] detectAndDecodeMulti started")

        retval, data, points,_ = detector.detectAndDecodeMulti(image)

        results = []

        if data:
            for text in data:
                if text:
                    results.append(text)
                    logger.info(f"[QR] detected: {text}")

        # fallback single QR
        if not results:
            text, _, _ = detector.detectAndDecode(image)
            if text:
                results.append(text)
                logger.info(f"[QR] fallback result: {text}")

        logger.info("[END] read_qr_opencv finished successfully")
        return results

    except Exception as e:
        logger.error(f"[ERROR] error reading QR code: {str(e)}")
        raise e


def process_qr(image, data):
    try:
        results = []
        boxes = data.get("boxes", [])

        logger.info(f"[PROCESS] start process_qr with {len(boxes)} boxes")

        h_img, w_img = image.shape[:2]

        for box in boxes:
            x, y, w, h = box["x"], box["y"], box["w"], box["h"]

            # safe crop bounds
            x1 = max(0, int(x))
            y1 = max(0, int(y))
            x2 = min(w_img, int(x + w))
            y2 = min(h_img, int(y + h))

            crop = image[y1:y2, x1:x2]

            if crop.size == 0:
                logger.warning(f"[QR] empty crop for box {box}")
                continue

            qr_data, points, _= detector.detectAndDecode(crop)

            ## si falla al recortar la imagen
            if not qr_data:
                qr_data = read_qr_opencv(image)
            logger.info(f"[QR] detected: {qr_data}")

            results.append({
                "label": box.get("label"),
                "x": x,
                "y": y,
                "qr_data": qr_data if qr_data else None
            })

            # DEBUG (opcional)
            debug = image.copy()
            cv2.rectangle(debug, (x1, y1), (x2, y2), (0, 255, 0), 2)

            filename = f"test/debug_box_{int(time.time() * 1000)}.jpg"
            cv2.imwrite(filename, debug)

        logger.info("[PROCESS] process_qr finished successfully")
        return results

    except Exception as e:
        logger.error(f"[ERROR] error processing box: {str(e)}")
        raise e