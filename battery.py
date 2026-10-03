# ============================================================
import os
from dotenv import load_dotenv

load_dotenv()
# BATTERY MONITORING SYSTEM
# Python + InfluxDB + Grafana
# ============================================================

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# ============================================================
# INFLUXDB CONFIGURATION
# ============================================================

INFLUX_URL = "http://localhost:8086"

# IMPORTANT:
# Put your NEW InfluxDB token here.
# Do NOT use the token visible in your screenshot.
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

INFLUX_ORG = "my-org"
INFLUX_BUCKET = "battery_monitor"


# ============================================================
# BATTERY THRESHOLDS
# ============================================================

# Absolute cell voltage reference limits
MIN_CELL_VOLTAGE = 2.8
MAX_CELL_VOLTAGE = 4.2

# Cell-to-cell voltage imbalance
WARNING_IMBALANCE = 0.10
CRITICAL_IMBALANCE = 0.20

# Temperature reference limits
MIN_CELL_TEMPERATURE = 22.0
MAX_CELL_TEMPERATURE = 38.0

# Critical temperature
CRITICAL_TEMPERATURE = 85.0


# ============================================================
# CONNECT TO INFLUXDB
# ============================================================

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(
    write_options=SYNCHRONOUS
)


# ============================================================
# SAFE NUMBER INPUT
# ============================================================

def get_number(prompt):
    """
    Ask the user for a number.

    If the user enters something invalid, the program does NOT
    crash. It asks again.
    """

    while True:

        try:
            value = input(prompt).strip()

            # Empty input
            if value == "":
                print("Please enter a numeric value.")
                continue

            return float(value)

        except ValueError:

            print()
            print("INVALID INPUT")
            print("Please enter ONLY a number.")
            print("Example: 3.7")
            print()

        except KeyboardInterrupt:

            print()
            print("Program stopped by user.")
            raise SystemExit


# ============================================================
# GET BATTERY INPUT
# ============================================================

def get_battery_input():

    print()
    print("=" * 60)
    print("BATTERY INPUT")
    print("=" * 60)

    print()
    print("Enter the battery measurements.")
    print("Example voltage: 3.7")
    print("Example current: 2.5")
    print("Example temperature: 30")
    print()

    # --------------------------------------------------------
    # CELL VOLTAGES
    # --------------------------------------------------------

    cell1 = get_number("Enter Cell 1 Voltage (V): ")
    cell2 = get_number("Enter Cell 2 Voltage (V): ")
    cell3 = get_number("Enter Cell 3 Voltage (V): ")
    cell4 = get_number("Enter Cell 4 Voltage (V): ")

    # --------------------------------------------------------
    # BATTERY CURRENT
    # --------------------------------------------------------

    current = get_number("Enter Battery Current (A): ")

    # --------------------------------------------------------
    # CELL TEMPERATURES
    # --------------------------------------------------------

    temp1 = get_number("Enter Cell 1 Temperature (°C): ")
    temp2 = get_number("Enter Cell 2 Temperature (°C): ")
    temp3 = get_number("Enter Cell 3 Temperature (°C): ")
    temp4 = get_number("Enter Cell 4 Temperature (°C): ")

    return (
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
    # CELL VOLTAGE STATUS
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
    # TEMPERATURE STATUS
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

    # Default states
    fan = "OFF"
    relay = "ON"
    buzzer = "OFF"
    led = "GREEN"

    battery_status = analysis["battery_status"]
    temperature_status = analysis["temperature_status"]
    imbalance_status = analysis["imbalance_status"]

    # --------------------------------------------------------
    # CRITICAL CONDITION
    # --------------------------------------------------------

    if battery_status == "CRITICAL":

        relay = "OFF"
        buzzer = "ON"
        led = "RED"

    # --------------------------------------------------------
    # WARNING CONDITION
    # --------------------------------------------------------

    elif battery_status == "WARNING":

        buzzer = "ON"
        led = "YELLOW"

    # --------------------------------------------------------
    # FAN CONTROL
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

    # --------------------------------------------------------
    # VOLTAGE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CURRENT
    # --------------------------------------------------------

    print()
    print("BATTERY CURRENT")
    print("-" * 60)

    print(f"Current : {current:.3f} A")

    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

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
    # WARNINGS
    # --------------------------------------------------------

    if analysis["voltage_anomalies"]:

        print()
        print("VOLTAGE WARNINGS")
        print("-" * 60)

        for warning in analysis["voltage_anomalies"]:
            print("WARNING:", warning)

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

        # ----------------------------------------------------
        # CELL VOLTAGES
        # ----------------------------------------------------

        .field("cell1_voltage", cell1)
        .field("cell2_voltage", cell2)
        .field("cell3_voltage", cell3)
        .field("cell4_voltage", cell4)

        # ----------------------------------------------------
        # CURRENT
        # ----------------------------------------------------

        .field("current", current)

        # ----------------------------------------------------
        # CELL TEMPERATURES
        # ----------------------------------------------------

        .field("cell1_temperature", temp1)
        .field("cell2_temperature", temp2)
        .field("cell3_temperature", temp3)
        .field("cell4_temperature", temp4)

        # ----------------------------------------------------
        # VOLTAGE ANALYSIS
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # TEMPERATURE ANALYSIS
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # STATUS TEXT
        #
        # New field names avoid the old integer/string
        # conflict you previously had in InfluxDB.
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # ACTUATOR TEXT
        # ----------------------------------------------------

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
# MAIN PROGRAM
# ============================================================

def main():

    print()
    print("=" * 60)
    print("BATTERY MONITORING SYSTEM")
    print("=" * 60)

    # --------------------------------------------------------
    # GET INPUT
    # --------------------------------------------------------

    (
        cell1,
        cell2,
        cell3,
        cell4,
        current,
        temp1,
        temp2,
        temp3,
        temp4
    ) = get_battery_input()

    # --------------------------------------------------------
    # ANALYZE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ACTUATORS
    # --------------------------------------------------------

    actuators = control_actuators(
        analysis
    )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # INFLUXDB
    # --------------------------------------------------------

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


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print("Program stopped.")

    finally:

        client.close()