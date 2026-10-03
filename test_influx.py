from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# ============================================================
# INFLUXDB SETTINGS
# ============================================================

INFLUX_URL = "http://localhost:8086"

INFLUX_TOKEN = "uSbZddWqcOenMhgYrif6c3FHAG3dgQMCzR7Tz29PHvXlB-5KQ5aj5e8XrEkTH7hKXX-quXMT4jRHszJ_XwJyng=="

INFLUX_ORG = "my-org"

INFLUX_BUCKET = "battery_monitor"


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
# TEST BATTERY DATA
# ============================================================

point = (
    Point("battery")
    .field("cell1_voltage", 4.12)
    .field("cell2_voltage", 4.11)
    .field("cell3_voltage", 4.10)
    .field("cell4_voltage", 4.09)
    .field("current", 1.20)
    .field("cell1_temperature", 29.0)
    .field("cell2_temperature", 30.0)
    .field("cell3_temperature", 30.0)
    .field("cell4_temperature", 31.0)
    .field("voltage_imbalance", 0.03)
    .field("average_voltage", 4.105)
    .field("max_temperature", 31.0)
    .field("system_status", 0)
    .field("charging_status", 1)
    .field("fan_status", 0)
    .field("protection_status", 0)
)


# ============================================================
# WRITE DATA
# ============================================================

try:

    write_api.write(
        bucket=INFLUX_BUCKET,
        org=INFLUX_ORG,
        record=point
    )

    print("SUCCESS: Data written to InfluxDB.")

except Exception as e:

    print("ERROR:")
    print(e)


# ============================================================
# CLOSE CONNECTION
# ============================================================

client.close()