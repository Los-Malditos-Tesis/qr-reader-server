import requests
import logging

logger = logging.getLogger("iot-opencv-service")

class qr_client():
    def __init__(self, base_url):
        self.base_url = base_url

    def send_qr_data(self, payload: dict):
        try:
            logger.info(f"[CLIENT] sending QR data to {self.base_url}")

            response = requests.post(
                f"{self.base_url}/qr-data",
                json=payload,
                timeout=10
            )

            logger.info(f"[CLIENT] response status={response.status_code}")

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"[CLIENT ERROR] {str(e)}")
            return None