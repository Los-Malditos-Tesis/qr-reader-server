import cv2
import numpy as np
from pyzbar.pyzbar import decode
from src.log.logger import logger
from src.utils.utils import upload_debug_image
from src.config.setting import settings

detector = cv2.QRCodeDetector()


# =========================
# WARP PERSPECTIVE
# =========================
def warp_qr(image, pts):

    pts = np.array(pts, dtype="float32")

    width = 700
    height = 700

    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(pts, dst)

    warped = cv2.warpPerspective(
        image,
        matrix,
        (width, height)
    )

    return warped


# =========================
# PREPROCESS
# =========================
def preprocess_image(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # upscale agresivo
    gray = cv2.resize(
        gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_LANCZOS4
    )

    # mejorar contraste
    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    # sharpen suave
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    gray = cv2.filter2D(gray, -1, kernel)

    # preservar bordes
    gray = cv2.bilateralFilter(gray, 7, 50, 50)

    # morphology close
    morph_kernel = np.ones((2, 2), np.uint8)

    gray = cv2.morphologyEx(
        gray,
        cv2.MORPH_CLOSE,
        morph_kernel
    )

    # adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        3
    )

    return adaptive


# =========================
# TRY MULTIPLE DECODES
# =========================
def try_decode_all(image):

    decoded = decode(image)

    if decoded:
        return decoded

    rotations = [
        cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(image, cv2.ROTATE_180),
        cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    ]

    for rotated in rotations:

        decoded = decode(rotated)

        if decoded:
            return decoded

    return []


# =========================
# EXTRACT RESULTS
# =========================
def extract_results(decoded, results):

    for obj in decoded:

        try:
            text = obj.data.decode("utf-8").strip()

            if text not in results:

                logger.info(f"[QR DETECTED] {text}")

                results.append(text)

        except Exception as e:
            logger.error(f"[DECODE ERROR] {str(e)}")


# =========================
# FIND QR CANDIDATES
# =========================
def find_qr_candidates(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        5
    )

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []

    for contour in contours:

        area = cv2.contourArea(contour)

        # ignorar pequeños
        if area < 1000:
            continue

        perimeter = cv2.arcLength(contour, True)

        approx = cv2.approxPolyDP(
            contour,
            0.04 * perimeter,
            True
        )

        # buscar cuadrados
        if len(approx) == 4:

            pts = approx.reshape(4, 2)

            candidates.append(pts)

    return candidates


# =========================
# MAIN FUNCTION
# =========================
def read_multiple_qr(image, correlationId, cameraCode):

    try:

        logger.info("[QR] STARTING DETECTION")
        if settings.DEVELOP_MODE == "DEBUG":
            image_url = upload_debug_image(image,"opencv-debug", correlationId, cameraCode)
            logger.info(f"[QR] Debug image uploaded: {image_url}")

        results = []
        results = []

        # ======================================
        # FIRST PASS - OpenCV Multi
        # ======================================

        retval, decoded_info, points, _ = detector.detectAndDecodeMulti(image)

        if retval and decoded_info:

            logger.info(f"[OpenCV] detected: {len(decoded_info)}")

            for text in decoded_info:

                if text and text not in results:

                    logger.info(f"[OpenCV QR] {text}")

                    results.append(text)

        # ======================================
        # SECOND PASS - pyzbar global
        # ======================================

        decoded = try_decode_all(image)

        extract_results(decoded, results)

        # ======================================
        # THIRD PASS - preprocess global
        # ======================================

        if len(results) < 3:

            logger.info("[QR] preprocess global")

            processed = preprocess_image(image)

            decoded = try_decode_all(processed)

            extract_results(decoded, results)

        # ======================================
        # FOURTH PASS - contour detection
        # ======================================

        if len(results) < 3:

            logger.info("[QR] contour scan")

            candidates = find_qr_candidates(image)

            logger.info(f"[QR] candidates: {len(candidates)}")

            for i, pts in enumerate(candidates):

                try:

                    warped = warp_qr(image, pts)

                    decoded = try_decode_all(warped)

                    if not decoded:

                        processed = preprocess_image(warped)

                        decoded = try_decode_all(processed)

                    extract_results(decoded, results)

                except Exception as contour_error:

                    logger.error(
                        f"[CONTOUR ERROR] {str(contour_error)}"
                    )

        logger.info(f"[QR] TOTAL DETECTED: {len(results)}")

        return results

    except Exception as e:

        logger.error(f"[QR ERROR] {str(e)}")

        return []
