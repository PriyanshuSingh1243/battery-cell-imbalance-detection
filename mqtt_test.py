import paho.mqtt.client as mqtt


# ============================================================
# MQTT SETTINGS
# ============================================================

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "battery/data"


# ============================================================
# WHEN PYTHON CONNECTS TO MOSQUITTO
# ============================================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    print("==========================================")
    print("CONNECTED TO MQTT BROKER")
    print("==========================================")

    print("Broker :", MQTT_BROKER)
    print("Port   :", MQTT_PORT)
    print("Topic  :", MQTT_TOPIC)

    # Subscribe to our battery topic
    client.subscribe(MQTT_TOPIC)

    print()
    print("Waiting for battery data...")
    print()


# ============================================================
# WHEN PYTHON RECEIVES AN MQTT MESSAGE
# ============================================================

def on_message(client, userdata, message):

    print("==========================================")
    print("MQTT DATA RECEIVED")
    print("==========================================")

    print("Topic:")
    print(message.topic)

    print()

    print("Message:")
    print(message.payload.decode("utf-8"))

    print()


# ============================================================
# CREATE MQTT CLIENT
# ============================================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)


# Tell MQTT what functions to call
client.on_connect = on_connect
client.on_message = on_message


# ============================================================
# CONNECT TO MOSQUITTO
# ============================================================

print("Connecting to MQTT broker...")

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)


# ============================================================
# KEEP LISTENING
# ============================================================

client.loop_forever()