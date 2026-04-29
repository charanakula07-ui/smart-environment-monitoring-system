#!/usr/bin/env python3
# =============================================================
#  Smart Environmental Monitoring System
#  Run     : python3 smart_monitor.py
# =============================================================

import RPi.GPIO as GPIO         # GPIO control (LED, buzzer)
import board                    # To access Raspberry Pi pin (D4)
import adafruit_dht             # Library for DHT11 sensor
import requests                 # For cloud upload (ThingSpeak)
import time                     # For delay between readings
import csv                      # Used to store sensor data in CSV file
import json                     # To read configuration file
from datetime import datetime   # Used to generate timestamp for each reading

# =============================================================
#  SECTION 1 — LOAD SETTINGS FROM config.json
# =============================================================
with open("config.json", "r") as f:
    config = json.load(f)

API_KEY        = config["thingspeak_api_key"]       # ThingSpeak Write API Key
TEMP_THRESHOLD = config["temperature_threshold"]    # Alert temperature limit (°C)

# =============================================================
#  SECTION 2 — PIN NUMBERS
# =============================================================
DHT_PIN    = board.D4   # GPIO4  — DHT11 Sensor
LDR_PIN    = 17         # GPIO17 — LDR Light Sensor
IR_PIN     = 27         # GPIO27 — IR Proximity Sensor
BUZZER_PIN = 18         # GPIO18 — Buzzer
LED1_PIN   = 22         # GPIO22 — Alert LED (Temp/Light)
LED2_PIN   = 23         # GPIO23 — Alert LED (IR)

# =============================================================
#  SECTION 3 — GPIO SETUP
# =============================================================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LDR_PIN,    GPIO.IN)
GPIO.setup(IR_PIN,     GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED1_PIN,   GPIO.OUT)
GPIO.setup(LED2_PIN,   GPIO.OUT)

# All outputs OFF at start
GPIO.output(BUZZER_PIN, GPIO.LOW)
GPIO.output(LED1_PIN,   GPIO.LOW)
GPIO.output(LED2_PIN,   GPIO.LOW)

# DHT11 sensor object
dht = adafruit_dht.DHT11(DHT_PIN)

# =============================================================
#  SECTION 4 — CSV LOG FILE SETUP
# =============================================================
LOG_FILE = "sensor_log.csv"

with open(LOG_FILE, "w", newline="") as f:
    csv.writer(f).writerow([
        "Timestamp", "Temp_C", "Humidity_%",
        "Light", "IR", "Alert_Temp", "Alert_Light", "Alert_IR"
    ])

# =============================================================
#  SECTION 5 — CLOUD UPLOAD FUNCTION
# =============================================================
def upload_to_cloud(temp, hum):
    try:
        url = f"https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={hum}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.text.strip() != "0":
            print(f"  [INFO] Data transferred successfully to cloud  (Entry #{r.text.strip()})")
        else:
            print(f"  [WARN] Cloud upload failed — HTTP {r.status_code}")
    except Exception as e:
        print(f"  [ERROR] Cloud error — {e}")

# =============================================================
#  SECTION 6 — STARTUP BANNER
# =============================================================
print("=" * 55)
print("   Smart Environmental Monitoring System")
print(f"   Temp Threshold : {TEMP_THRESHOLD} C")
print("=" * 55)
print("   Running... Press Ctrl+C to stop.")
print("-" * 55)

# =============================================================
#  SECTION 7 — MAIN LOOP
# =============================================================
loop = 0

try:
    while True:
        loop += 1
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ── Read DHT11 ────────────────────────────────────────
        temp, hum = None, None
        try:
            temp = dht.temperature
            hum  = dht.humidity
        except RuntimeError:
            pass   # DHT11 sometimes misses a reading — ignore and retry

        # ── Read LDR (Light) ──────────────────────────────────
        light = "DARK" if GPIO.input(LDR_PIN) == 0 else "BRIGHT"

        # ── Read IR Sensor ────────────────────────────────────
        ir = GPIO.input(IR_PIN) == GPIO.LOW   # LOW = object detected

        # ── Check Alerts ──────────────────────────────────────
        alert_temp  = temp is not None and temp > TEMP_THRESHOLD
        alert_light = light == "DARK"
        alert_ir    = ir

        # ── Control LEDs ──────────────────────────────────────
        GPIO.output(LED1_PIN, GPIO.HIGH if (alert_temp or alert_light) else GPIO.LOW)
        GPIO.output(LED2_PIN, GPIO.HIGH if alert_ir else GPIO.LOW)

        # ── Buzzer beep on any alert ──────────────────────────
        if alert_temp or alert_light or alert_ir:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(BUZZER_PIN, GPIO.LOW)

        # ── Print to Terminal ─────────────────────────────────
        print(f"\n[{ts}]")
        if temp is not None:
            print(f"  Temp     : {temp} C   {'*** ALERT ***' if alert_temp else '[OK]'}")
            print(f"  Humidity : {hum} %")
        else:
            print("  Temp     : Warming up...")
            print("  Humidity : Warming up...")
        print(f"  Light    : {light}   {'*** DARK ALERT ***' if alert_light else ''}")
        print(f"  IR       : {'*** OBJECT DETECTED ***' if alert_ir else 'Clear [OK]'}")
        print("-" * 55)

        # ── Save to CSV ───────────────────────────────────────
        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow([
                ts,
                temp if temp else "ERR",
                hum  if hum  else "ERR",
                light,
                "YES" if alert_ir    else "NO",
                "YES" if alert_temp  else "NO",
                "YES" if alert_light else "NO",
                "YES" if alert_ir    else "NO",
            ])

        # ── Upload every 5 loops (~10 sec) ───────────────────
        if loop % 5 == 0 and temp is not None:
            upload_to_cloud(temp, hum)

        time.sleep(2)

except KeyboardInterrupt:
    print("\n[INFO] Stopped by user.")

finally:
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.output(LED1_PIN,   GPIO.LOW)
    GPIO.output(LED2_PIN,   GPIO.LOW)
    GPIO.cleanup()
    dht.exit()
    print("[INFO] GPIO cleaned up.")
