import cv2
import base64


def image_to_base64(image):

    success, buffer = cv2.imencode(".jpg", image)

    if not success:
        return None

    return base64.b64encode(buffer).decode("utf-8")