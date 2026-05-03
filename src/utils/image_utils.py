import cv2


def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Mejora contraste
    gray = cv2.equalizeHist(gray)

    # Reduce ruido
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    return blur


def resize_image(image, scale=2):
    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )