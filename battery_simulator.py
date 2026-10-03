import os
import ssl
import json
import time
import random
import getpass
import paho.mqtt.client as mqtt


# ============================================================
# MQTT / EMQX CLOUD CONFIGURATION
# ============================================================

MQTT_BROKER = "x8e621b5.ala.asia-southeast1.emqxsl.com"
MQTT_PORT = 8883
MQTT_TOPIC = "battery/data"

MQTT_USERNAME = "bms_device"

# Password is NOT stored in this file.
# It will be requested when the program starts if
# MQTT_PASSWORD is not already set in the terminal.
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

if not MQTT_PASSWORD:
    MQTT_PASSWORD = getpass.getpass("Enter EMQX MQTT password: ")


# ============================================================
# CONNECTION STATUS
# ============================================================

MQTT_CONNECTED = False


# ============================================================
# INITIAL BATTERY VALUES
# ============================================================

cell1_voltage = 4.12
cell2_voltage = 4.11
cell3_voltage = 4.09
cell4_voltage = 4.10

current = 2.50

cell1_temperature = 30.0
cell2_temperature = 31.0
cell3_temperature = 30.5
cell4_temperature = 31.5


# ============================================================
# MQTT CONNECT CALLBACK
# ============================================================

def on_connect(client, userdata, flags, reason_code, properties):

    global MQTT_CONNECTED

    if reason_code == 0:

        MQTT_CONNECTED = True

        print()
        print("=" * 60)
        print("BATTERY SIMULATOR CONNECTED TO EMQX CLOUD")
        print("=" * 60)
        print("Broker :", MQTT_BROKER)
        print("Port   :", MQTT_PORT)
        print("Topic  :", MQTT_TOPIC)
        print("User   :", MQTT_USERNAME)
        print("=" * 60)
        print()

    else:

        MQTT_CONNECTED = False

        print()
        print("MQTT CONNECTION FAILED")
        print("Reason code:", reason_code)
        print()


# ============================================================
# MQTT DISCONNECT CALLBACK
# ============================================================

def on_disconnect(
    client,
    userdata,
    disconnect_flags,
    reason_code,
    properties
):

    global MQTT_CONNECTED

    MQTT_CONNECTED = False

    print()
    print("Disconnected from EMQX Cloud.")
    print("Reason code:", reason_code)
    print("Waiting for automatic reconnection...")
    print()


# ============================================================
# MQTT CLIENT
# ============================================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="battery_simulator_01"
)


# ============================================================
# MQTT AUTHENTICATION
# ============================================================

client.username_pw_set(
    username=MQTT_USERNAME,
    password=MQTT_PASSWORD
)


# ============================================================
# TLS / SSL
# ============================================================

client.tls_set(
    cert_reqs=ssl.CERT_REQUIRED
)


# ============================================================
# RECONNECTION SETTINGS
# ============================================================

client.reconnect_delay_set(
    min_delay=1,
    max_delay=30
)


# ============================================================
# CALLBACKS
# ============================================================

client.on_connect = on_connect
client.on_disconnect = on_disconnect


# ============================================================
# CONNECT TO EMQX
# ============================================================

print()
print("=" * 60)
print("CONNECTING TO EMQX CLOUD...")
print("=" * 60)

try:

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        keepalive=60
    )

except Exception as e:

    print()
    print("ERROR: Could not connect to EMQX Cloud.")
    print("Reason:", e)
    print()
    raise SystemExit(1)


# ============================================================
# START MQTT NETWORK LOOP
# ============================================================

client.loop_start()


# ============================================================
# WAIT UNTIL CONNECTION IS READY
# ============================================================

print("Waiting for MQTT connection...")

connection_wait_start = time.time()

while not MQTT_CONNECTED:

    time.sleep(0.2)

    # Prevent infinite waiting
    if time.time() - connection_wait_start > 30:

        print()
        print("ERROR: MQTT connection timeout.")
        print("Check:")
        print("1. EMQX deployment is running")
        print("2. Username/password are correct")
        print("3. Port is 8883")
        print("4. TLS is enabled")
        print()

        client.loop_stop()
        client.disconnect()

        raise SystemExit(1)


print("MQTT connection is ready.")
print()
print("Starting continuous battery telemetry...")
print("Press CTRL+C to stop.")
print()


# ============================================================
# BATTERY SIMULATION
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # CHECK MQTT CONNECTION
        # ----------------------------------------------------

        if not MQTT_CONNECTED:

            print("MQTT disconnected.")
            print("Waiting for reconnection...")

            time.sleep(2)

            continue


        # ----------------------------------------------------
        # SLOWLY CHANGE CELL VOLTAGES
        # ----------------------------------------------------

        cell1_voltage += random.uniform(-0.003, 0.003)
        cell2_voltage += random.uniform(-0.003, 0.003)
        cell3_voltage += random.uniform(-0.003, 0.003)
        cell4_voltage += random.uniform(-0.003, 0.003)


        # Keep voltage in realistic range

        cell1_voltage = max(
            3.70,
            min(4.20, cell1_voltage)
        )

        cell2_voltage = max(
            3.70,
            min(4.20, cell2_voltage)
        )

        cell3_voltage = max(
            3.70,
            min(4.20, cell3_voltage)
        )

        cell4_voltage = max(
            3.70,
            min(4.20, cell4_voltage)
        )


        # ----------------------------------------------------
        # CHANGE PACK CURRENT
        # ----------------------------------------------------

        current += random.uniform(-0.20, 0.20)

        current = max(
            1.0,
            min(5.0, current)
        )


        # ----------------------------------------------------
        # CHANGE CELL TEMPERATURES
        # ----------------------------------------------------

        cell1_temperature += random.uniform(-0.3, 0.3)
        cell2_temperature += random.uniform(-0.3, 0.3)
        cell3_temperature += random.uniform(-0.3, 0.3)
        cell4_temperature += random.uniform(-0.3, 0.3)


        # Keep temperatures realistic

        cell1_temperature = max(
            25.0,
            min(37.0, cell1_temperature)
        )

        cell2_temperature = max(
            25.0,
            min(37.0, cell2_temperature)
        )

        cell3_temperature = max(
            25.0,
            min(37.0, cell3_temperature)
        )

        cell4_temperature = max(
            25.0,
            min(37.0, cell4_temperature)
        )


        # ----------------------------------------------------
        # CREATE BATTERY TELEMETRY
        # ----------------------------------------------------

        battery_data = {

            "cell1_voltage": round(cell1_voltage, 3),
            "cell2_voltage": round(cell2_voltage, 3),
            "cell3_voltage": round(cell3_voltage, 3),
            "cell4_voltage": round(cell4_voltage, 3),

            "current": round(current, 2),

            "cell1_temperature": round(
                cell1_temperature,
                1
            ),

            "cell2_temperature": round(
                cell2_temperature,
                1
            ),

            "cell3_temperature": round(
                cell3_temperature,
                1
            ),

            "cell4_temperature": round(
                cell4_temperature,
                1
            )
        }


        # ----------------------------------------------------
        # CONVERT DATA TO JSON
        # ----------------------------------------------------

        payload = json.dumps(battery_data)


        # ----------------------------------------------------
        # PUBLISH DATA TO EMQX
        # ----------------------------------------------------

        result = client.publish(
            MQTT_TOPIC,
            payload,
            qos=1
        )


        # ----------------------------------------------------
        # CHECK PUBLISH RESULT
        # ----------------------------------------------------

        if result.rc == mqtt.MQTT_ERR_SUCCESS:

            print("Battery telemetry published:")
            print(payload)
            print()

        else:

            print()
            print("Publish failed.")
            print("Error code:", result.rc)
            print()


        # ----------------------------------------------------
        # WAIT BEFORE NEXT READING
        # ----------------------------------------------------

        time.sleep(2)


# ============================================================
# STOP WITH CTRL+C
# ============================================================

except KeyboardInterrupt:

    print()
    print("=" * 60)
    print("STOPPING BATTERY SIMULATOR...")
    print("=" * 60)


# ============================================================
# CLEAN SHUTDOWN
# ============================================================

finally:

    client.loop_stop()

    if client.is_connected():
        client.disconnect()

    print("Simulator stopped.")