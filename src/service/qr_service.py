import cv2
from src.utils.image_utils import preprocess, resize_image

detector = cv2.QRCodeDetector()


def read_qr_opencv(image):
    data, points, _ = detector.detectAndDecodeMulti(image)

    results = []

    if points is not None:
        for text in data:
            if text:
                results.append(text)

    # fallback a single
    if not results:
        text, _, _ = detector.detectAndDecode(image)
        if text:
            results.append(text)

    return results


def process_qr(image, boxes):
    all_results = []

    for box in boxes:
        x, y, w, h = box["x"], box["y"], box["w"], box["h"]

        roi = image[y:y + h, x:x + w]

        # mejora clave
        roi = resize_image(roi)
        processed = preprocess(roi)

        qr_data_list = read_qr_opencv(processed)

        all_results.append({
            "box": box,
            "data": qr_data_list
        })

    return all_results