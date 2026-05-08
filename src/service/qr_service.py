import cv2
import numpy as np
from pyzbar.pyzbar import decode
from src.log.logger import logger

detector = cv2.QRCodeDetector()


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # aumentar tamaño
    gray = cv2.resize(
        gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # CLAHE
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    # mejorar contraste
    gray = cv2.convertScaleAbs(
        gray,
        alpha=1.8,
        beta=30
    )

    # blur suave
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # threshold adaptativo
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        5
    )

    return gray, thresh


def extract_results(decoded, results):
    for obj in decoded:
        text = obj.data.decode("utf-8")

        if text not in results:
            logger.info(f"[QR] detected: {text}")
            results.append(text)


def read_multiple_qr(image):
    try:
        logger.info("[QR] starting detection")

        gray, thresh = preprocess_image(image)

        results = []

        # intento 1: imagen original
        decoded = decode(image)
        extract_results(decoded, results)

        # intento 2: grayscale
        if not results:
            decoded = decode(gray)
            extract_results(decoded, results)

        # intento 3: threshold
        if not results:
            decoded = decode(thresh)
            extract_results(decoded, results)

        # fallback OpenCV
        if not results:
            retval, data, points, _ = detector.detectAndDecodeMulti(thresh)

            if retval and data:
                for text in data:
                    if text and text not in results:
                        logger.info(f"[OpenCV QR] {text}")
                        results.append(text)

        # debug
        cv2.imwrite("test/debug_gray.jpg", gray)
        cv2.imwrite("test/debug_thresh.jpg", thresh)

        logger.info(f"[QR] detected {len(results)} QR")

        return results

    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        return []