# ============================================================
from dotenv import load_dotenv

load_dotenv()
# BATTERY MQTT CLOUD MONITORING SYSTEM
# Python + MQTT + EMQX Cloud + InfluxDB + Grafana
# ============================================================

import json
import os

import paho.mqtt.client as mqtt

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# ============================================================
# MQTT CONFIGURATION - EMQX CLOUD
# ============================================================

MQTT_BROKER = "x8e621b5.ala.asia-southeast1.emqxsl.com"
MQTT_PORT = 8883
MQTT_TOPIC = "battery/data"

# Keep password private.
# Set this as an environment variable:
# MQTT_PASSWORD=your_emqx_password
MQTT_USERNAME = "bms_device"
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")


# ============================================================
# INFLUXDB CONFIGURATION
# ============================================================

# For now, keep using your existing local InfluxDB.
# Later we can move this to InfluxDB Cloud.

INFLUX_URL = "http://localhost:8086"

# Set your existing InfluxDB token as an environment variable:
# INFLUX_TOKEN=your_token
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

INFLUX_ORG = "my-org"
INFLUX_BUCKET = "battery_monitor"


# ============================================================
# BATTERY THRESHOLDS
# ============================================================

MIN_CELL_VOLTAGE = 2.8
MAX_CELL_VOLTAGE = 4.2

WARNING_IMBALANCE = 0.10
CRITICAL_IMBALANCE = 0.20

MIN_CELL_TEMPERATURE = 22.0
MAX_CELL_TEMPERATURE = 38.0

CRITICAL_TEMPERATURE = 85.0


# ============================================================
# CONNECT TO INFLUXDB
# ============================================================

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx_client.write_api(
    write_options=SYNCHRONOUS
)


# ============================================================
# BATTERY ANALYSIS
# ============================================================

def analyze_battery(
    cell1,
    cell2,
    cell3,
    cell4,
    current,
    temp1,
    temp2,
    temp3,
    temp4
):

    voltages = [
        cell1,
        cell2,
        cell3,
        cell4
    ]

    temperatures = [
        temp1,
        temp2,
        temp3,
        temp4
    ]

    # --------------------------------------------------------
    # VOLTAGE CALCULATIONS
    # --------------------------------------------------------

    maximum_voltage = max(voltages)
    minimum_voltage = min(voltages)
    average_voltage = sum(voltages) / len(voltages)

    voltage_imbalance = (
        maximum_voltage - minimum_voltage
    )

    # --------------------------------------------------------
    # VOLTAGE ANOMALIES
    # --------------------------------------------------------

    voltage_anomalies = []

    for index, voltage in enumerate(voltages, start=1):

        if voltage < MIN_CELL_VOLTAGE:

            voltage_anomalies.append(
                f"Cell {index} LOW VOLTAGE"
            )

        elif voltage > MAX_CELL_VOLTAGE:

            voltage_anomalies.append(
                f"Cell {index} HIGH VOLTAGE"
            )

    # --------------------------------------------------------
    # IMBALANCE STATUS
    # --------------------------------------------------------

    if voltage_imbalance > CRITICAL_IMBALANCE:

        imbalance_status = "CRITICAL"

    elif voltage_imbalance > WARNING_IMBALANCE:

        imbalance_status = "WARNING"

    else:

        imbalance_status = "NORMAL"

    # --------------------------------------------------------
    # TEMPERATURE CALCULATIONS
    # --------------------------------------------------------

    maximum_temperature = max(temperatures)
    minimum_temperature = min(temperatures)
    average_temperature = sum(temperatures) / len(temperatures)

    # --------------------------------------------------------
    # TEMPERATURE ANOMALIES
    # --------------------------------------------------------

    temperature_anomalies = []

    for index, temperature in enumerate(
        temperatures,
        start=1
    ):

        if temperature > CRITICAL_TEMPERATURE:

            temperature_anomalies.append(
                f"Cell {index} CRITICAL TEMPERATURE"
            )

        elif temperature > MAX_CELL_TEMPERATURE:

            temperature_anomalies.append(
                f"Cell {index} HIGH TEMPERATURE"
            )

        elif temperature < MIN_CELL_TEMPERATURE:

            temperature_anomalies.append(
                f"Cell {index} LOW TEMPERATURE"
            )

    # --------------------------------------------------------
    # TEMPERATURE STATUS
    # --------------------------------------------------------

    if maximum_temperature > CRITICAL_TEMPERATURE:

        temperature_status = "CRITICAL"

    elif maximum_temperature > MAX_CELL_TEMPERATURE:

        temperature_status = "WARNING"

    else:

        temperature_status = "NORMAL"

    # --------------------------------------------------------
    # OVERALL BATTERY STATUS
    # --------------------------------------------------------

    if (
        len(voltage_anomalies) > 0
        or temperature_status == "CRITICAL"
        or imbalance_status == "CRITICAL"
    ):

        battery_status = "CRITICAL"

    elif (
        temperature_status == "WARNING"
        or imbalance_status == "WARNING"
        or len(voltage_anomalies) > 0
        or len(temperature_anomalies) > 0
    ):

        battery_status = "WARNING"

    else:

        battery_status = "NORMAL"

    return {

        "maximum_voltage": maximum_voltage,
        "minimum_voltage": minimum_voltage,
        "average_voltage": average_voltage,
        "voltage_imbalance": voltage_imbalance,

        "voltage_anomalies": voltage_anomalies,

        "imbalance_status": imbalance_status,

        "average_temperature": average_temperature,
        "maximum_temperature": maximum_temperature,
        "minimum_temperature": minimum_temperature,

        "temperature_anomalies": temperature_anomalies,

        "temperature_status": temperature_status,

        "battery_status": battery_status
    }


# ============================================================
# ACTUATOR CONTROL
# ============================================================

def control_actuators(analysis):

    fan = "OFF"
    relay = "ON"
    buzzer = "OFF"
    led = "GREEN"

    battery_status = analysis["battery_status"]
    temperature_status = analysis["temperature_status"]

    # --------------------------------------------------------
    # CRITICAL
    # --------------------------------------------------------

    if battery_status == "CRITICAL":

        relay = "OFF"
        buzzer = "ON"
        led = "RED"

    # --------------------------------------------------------
    # WARNING
    # --------------------------------------------------------

    elif battery_status == "WARNING":

        buzzer = "ON"
        led = "YELLOW"

    # --------------------------------------------------------
    # FAN
    # --------------------------------------------------------

    if temperature_status in [
        "WARNING",
        "CRITICAL"
    ]:

        fan = "ON"

    return {
        "fan": fan,
        "relay": relay,
        "buzzer": buzzer,
        "led": led
    }


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_output(
    cell1,
    cell2,
    cell3,
    cell4,
    current,
    temp1,
    temp2,
    temp3,
    temp4,
    analysis,
    actuators
):

    print()
    print("=" * 60)
    print("BATTERY MONITORING RESULTS")
    print("=" * 60)

    print()
    print("CELL VOLTAGES")
    print("-" * 60)

    print(f"Cell 1 : {cell1:.3f} V")
    print(f"Cell 2 : {cell2:.3f} V")
    print(f"Cell 3 : {cell3:.3f} V")
    print(f"Cell 4 : {cell4:.3f} V")

    print()

    print(
        f"Maximum Voltage : "
        f"{analysis['maximum_voltage']:.3f} V"
    )

    print(
        f"Minimum Voltage : "
        f"{analysis['minimum_voltage']:.3f} V"
    )

    print(
        f"Average Voltage : "
        f"{analysis['average_voltage']:.3f} V"
    )

    print(
        f"Voltage Imbalance : "
        f"{analysis['voltage_imbalance']:.3f} V"
    )

    print()
    print("BATTERY CURRENT")
    print("-" * 60)

    print(f"Current : {current:.3f} A")

    print()
    print("CELL TEMPERATURES")
    print("-" * 60)

    print(f"Cell 1 : {temp1:.2f} °C")
    print(f"Cell 2 : {temp2:.2f} °C")
    print(f"Cell 3 : {temp3:.2f} °C")
    print(f"Cell 4 : {temp4:.2f} °C")

    print()

    print(
        f"Maximum Temperature : "
        f"{analysis['maximum_temperature']:.2f} °C"
    )

    print(
        f"Minimum Temperature : "
        f"{analysis['minimum_temperature']:.2f} °C"
    )

    print(
        f"Average Temperature : "
        f"{analysis['average_temperature']:.2f} °C"
    )

    print()
    print("STATUS")
    print("-" * 60)

    print(
        f"Battery Status     : "
        f"{analysis['battery_status']}"
    )

    print(
        f"Voltage Imbalance  : "
        f"{analysis['imbalance_status']}"
    )

    print(
        f"Temperature Status : "
        f"{analysis['temperature_status']}"
    )

    # --------------------------------------------------------
    # VOLTAGE WARNINGS
    # --------------------------------------------------------

    if analysis["voltage_anomalies"]:

        print()
        print("VOLTAGE WARNINGS")
        print("-" * 60)

        for warning in analysis["voltage_anomalies"]:

            print("WARNING:", warning)

    # --------------------------------------------------------
    # TEMPERATURE WARNINGS
    # --------------------------------------------------------

    if analysis["temperature_anomalies"]:

        print()
        print("TEMPERATURE WARNINGS")
        print("-" * 60)

        for warning in analysis["temperature_anomalies"]:

            print("WARNING:", warning)

    # --------------------------------------------------------
    # ACTUATORS
    # --------------------------------------------------------

    print()
    print("ACTUATORS")
    print("-" * 60)

    print(f"Cooling Fan : {actuators['fan']}")
    print(f"Relay       : {actuators['relay']}")
    print(f"Buzzer      : {actuators['buzzer']}")
    print(f"LED         : {actuators['led']}")

    print()
    print("=" * 60)


# ============================================================
# SEND DATA TO INFLUXDB
# ============================================================

def send_to_influxdb(
    cell1,
    cell2,
    cell3,
    cell4,
    current,
    temp1,
    temp2,
    temp3,
    temp4,
    analysis,
    actuators
):

    point = (

        Point("battery")

        .field("cell1_voltage", cell1)
        .field("cell2_voltage", cell2)
        .field("cell3_voltage", cell3)
        .field("cell4_voltage", cell4)

        .field("current", current)

        .field("cell1_temperature", temp1)
        .field("cell2_temperature", temp2)
        .field("cell3_temperature", temp3)
        .field("cell4_temperature", temp4)

        .field(
            "maximum_voltage",
            analysis["maximum_voltage"]
        )

        .field(
            "minimum_voltage",
            analysis["minimum_voltage"]
        )

        .field(
            "average_voltage",
            analysis["average_voltage"]
        )

        .field(
            "voltage_imbalance",
            analysis["voltage_imbalance"]
        )

        .field(
            "maximum_temperature",
            analysis["maximum_temperature"]
        )

        .field(
            "minimum_temperature",
            analysis["minimum_temperature"]
        )

        .field(
            "average_temperature",
            analysis["average_temperature"]
        )

        .field(
            "battery_status_text",
            analysis["battery_status"]
        )

        .field(
            "imbalance_status_text",
            analysis["imbalance_status"]
        )

        .field(
            "temperature_status_text",
            analysis["temperature_status"]
        )

        .field(
            "fan_state_text",
            actuators["fan"]
        )

        .field(
            "relay_state_text",
            actuators["relay"]
        )

        .field(
            "buzzer_state_text",
            actuators["buzzer"]
        )

        .field(
            "led_state_text",
            actuators["led"]
        )
    )

    try:

        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )

        print()
        print("Data successfully sent to InfluxDB.")

    except Exception as error:

        print()
        print("ERROR: Could not send data to InfluxDB.")
        print(error)


# ============================================================
# MQTT MESSAGE RECEIVED
# ============================================================

def on_message(client, userdata, message):

    print()
    print("=" * 60)
    print("MQTT DATA RECEIVED")
    print("=" * 60)

    try:

        payload = message.payload.decode("utf-8")

        print("Topic:", message.topic)
        print("Message:", payload)

        # ----------------------------------------------------
        # CONVERT JSON TEXT TO PYTHON DICTIONARY
        # ----------------------------------------------------

        data = json.loads(payload)

        # ----------------------------------------------------
        # GET VALUES
        # ----------------------------------------------------

        cell1 = float(data["cell1_voltage"])
        cell2 = float(data["cell2_voltage"])
        cell3 = float(data["cell3_voltage"])
        cell4 = float(data["cell4_voltage"])

        current = float(data["current"])

        temp1 = float(data["cell1_temperature"])
        temp2 = float(data["cell2_temperature"])
        temp3 = float(data["cell3_temperature"])
        temp4 = float(data["cell4_temperature"])

        # ----------------------------------------------------
        # ANALYZE BATTERY
        # ----------------------------------------------------

        analysis = analyze_battery(
            cell1,
            cell2,
            cell3,
            cell4,
            current,
            temp1,
            temp2,
            temp3,
            temp4
        )

        # ----------------------------------------------------
        # ACTUATORS
        # ----------------------------------------------------

        actuators = control_actuators(
            analysis
        )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        display_output(
            cell1,
            cell2,
            cell3,
            cell4,
            current,
            temp1,
            temp2,
            temp3,
            temp4,
            analysis,
            actuators
        )

        # ----------------------------------------------------
        # INFLUXDB
        # ----------------------------------------------------

        send_to_influxdb(
            cell1,
            cell2,
            cell3,
            cell4,
            current,
            temp1,
            temp2,
            temp3,
            temp4,
            analysis,
            actuators
        )

    except json.JSONDecodeError:

        print()
        print("ERROR: MQTT message is not valid JSON.")

    except KeyError as error:

        print()
        print("ERROR: Missing required battery field:")
        print(error)

    except ValueError as error:

        print()
        print("ERROR: Battery value is not numeric.")
        print(error)

    except Exception as error:

        print()
        print("ERROR while processing MQTT data:")
        print(error)


# ============================================================
# MQTT CONNECT
# ============================================================

def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties=None
):

    print()
    print("=" * 60)
    print("BATTERY MQTT CLOUD MONITORING SYSTEM")
    print("=" * 60)

    print()
    print("Connecting to EMQX Cloud...")

    if reason_code == 0:

        print()
        print("CONNECTED TO EMQX CLOUD")

        print()
        print("Broker :", MQTT_BROKER)
        print("Port   :", MQTT_PORT)
        print("Topic  :", MQTT_TOPIC)

        client.subscribe(MQTT_TOPIC)

        print()
        print("Subscribed to:", MQTT_TOPIC)
        print("Waiting for battery data...")
        print()

    else:

        print()
        print("MQTT CONNECTION FAILED")
        print("Reason code:", reason_code)


# ============================================================
# MQTT DISCONNECT
# ============================================================

def on_disconnect(
    client,
    userdata,
    disconnect_flags,
    reason_code,
    properties=None
):

    print()
    print("MQTT disconnected.")
    print("Reason code:", reason_code)


# ============================================================
# CREATE MQTT CLIENT
# ============================================================

mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="python_bms_cloud_monitor"
)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect


# ============================================================
# MQTT AUTHENTICATION
# ============================================================

if not MQTT_PASSWORD:

    print()
    print("WARNING:")
    print("MQTT_PASSWORD environment variable is not set.")
    print("Set it before running the program.")
    print()


mqtt_client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)


# ============================================================
# ENABLE TLS
# ============================================================

# EMQX Serverless uses MQTT over TLS on port 8883.

mqtt_client.tls_set()


# ============================================================
# MAIN
# ============================================================

try:

    print("Starting battery MQTT cloud monitor...")
    print()

    mqtt_client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    mqtt_client.loop_forever()

except KeyboardInterrupt:

    print()
    print("Program stopped by user.")

except Exception as error:

    print()
    print("ERROR: MQTT connection failed.")
    print(error)

finally:

    try:
        mqtt_client.disconnect()
    except Exception:
        pass

    influx_client.close()