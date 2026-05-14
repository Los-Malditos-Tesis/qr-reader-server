import os

class Setting:
    MQTT_SERVICE_URL = os.getenv("MQTT_SERVICE_URL")
    MQTT_SERVICE_PORT = int(os.getenv("MQTT_SERVICE_PORT", "1883"))

    MQTT_SERVICE_USERNAME = os.getenv("MQTT_SERVICE_USERNAME")
    MQTT_SERVICE_PASSWORD = os.getenv("MQTT_SERVICE_PASSWORD")

    MQTT_TOPIC_RESULT = os.getenv("MQTT_TOPIC_RESULT")
    DEVELOP_MODE = os.getenv("DEVELOP_MODE")

print(Setting.MQTT_SERVICE_URL)

settings = Setting()