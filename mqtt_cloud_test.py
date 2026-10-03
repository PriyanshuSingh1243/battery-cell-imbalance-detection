import ssl
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv()

MQTT_BROKER = "x8e621b5.ala.asia-southeast1.emqxsl.com"
MQTT_PORT = 8883

MQTT_USERNAME = "bms_device"
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

if not MQTT_PASSWORD:
    raise RuntimeError("MQTT_PASSWORD is not set in .env")

MQTT_TOPIC = "battery/data"


def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to EMQX Cloud!")
    print("Reason code:", reason_code)

    client.subscribe(MQTT_TOPIC)
    print("Subscribed to:", MQTT_TOPIC)


def on_message(client, userdata, msg):
    print("\nMessage received!")
    print("Topic:", msg.topic)
    print("Payload:", msg.payload.decode())


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="python_bms_test"
)

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.tls_set(
    cert_reqs=ssl.CERT_REQUIRED
)

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to EMQX Cloud...")

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    keepalive=60
)

client.loop_forever()