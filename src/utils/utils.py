import os
import cv2
import cloudinary
import cloudinary.uploader
from  src.config.setting import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


def upload_debug_image(image, folder="opencv-debug", correlationId = "", cameraCode = ""):

    path = "/tmp/debug_frame.jpg"

    success = cv2.imwrite(path, image)

    if not success:
        return None

    result = cloudinary.uploader.upload(
        path,
        folder=folder,
        public_id=f"{cameraCode}/{correlationId}",
    )

    return result.get("secure_url")