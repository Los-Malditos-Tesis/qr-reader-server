import os
import cv2
import cloudinary
import cloudinary.uploader
import  src.config.setting as setting

cloudinary.config(
    cloud_name=setting.settings.CLOUDINARY_CLOUD_NAME,
    api_key=setting.settings.CLOUDINARY_API_KEY,
    api_secret=setting.settings.CLOUDINARY_API_SECRET,
    secure=True
)


def upload_debug_image(image, folder="opencv-debug"):

    path = "/tmp/debug_frame.jpg"

    success = cv2.imwrite(path, image)

    if not success:
        return None

    result = cloudinary.uploader.upload(
        path,
        folder=folder
    )

    return result.get("secure_url")