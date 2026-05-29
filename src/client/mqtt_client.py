import json
import paho.mqtt.client as mqtt
from src.config.setting import settings
from src.log.logger import logger


class MQTTClientManager:
    def __init__(self):
        self.client = mqtt.Client(client_id="opencv-service-local")
        self.connected = False

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    # ----------------------------
    # EVENTS
    # ----------------------------
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("[MQTT] Connected successfully")
        else:
            logger.error(f"[MQTT] Connection failed rc={rc}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning(f"[MQTT] Disconnected rc={rc}")

    # ----------------------------
    # CONNECT
    # ----------------------------
    def connect(self):
        if not settings.MQTT_SERVICE_URL:
            raise ValueError("MQTT_SERVICE_URL no está definido")

        if settings.MQTT_SERVICE_USERNAME:
            self.client.username_pw_set(
                settings.MQTT_SERVICE_USERNAME,
                settings.MQTT_SERVICE_PASSWORD
            )

        import ssl
        self.client.tls_set(
            cert_reqs=ssl.CERT_REQUIRED
        )

        logger.info(f"[MQTT] Connecting to {settings.MQTT_SERVICE_URL}")

        self.client.connect(
            settings.MQTT_SERVICE_URL,
            settings.MQTT_SERVICE_PORT,
            60
        )

        self.client.loop_start()

    # ----------------------------
    # DISCONNECT
    # ----------------------------
    def disconnect(self):
        logger.info("[MQTT] Disconnecting...")
        self.client.loop_stop()
        self.client.disconnect()

    # ----------------------------
    # PUBLISH
    # ----------------------------
    def publish(self, topic: str, payload: dict):
        if not self.connected:
            logger.warning("[MQTT] Not connected, skipping publish")
            return

        message = json.dumps(payload)

        result = self.client.publish(topic, message, qos=1)

        logger.info(f"[MQTT] Published to {topic} rc={result.rc}")


# Singleton (única instancia)
mqtt_manager = MQTTClientManager()