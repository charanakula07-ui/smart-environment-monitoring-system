#  Smart Environmental Monitoring System

##  Overview
The Smart Environmental Monitoring System is an IoT-based solution developed using Raspberry Pi and Python to continuously monitor environmental conditions in real time.  
It captures parameters such as temperature, humidity, light intensity, and motion, and provides both **local alerts** and **cloud-based monitoring** using ThingSpeak.

---

##  Key Features
-  Real-time monitoring of environmental parameters  
-  Cloud integration using ThingSpeak for remote access  
-  Automatic data logging into CSV files  
-  Alert system using LED indicators and buzzer  
-  Threshold-based temperature monitoring  
-  Continuous data acquisition with periodic updates  

---

## Technologies & Components
- **Programming Language:** Python  
- **Hardware:** Raspberry Pi  
- **Sensors Used:**  
  - DHT11 (Temperature & Humidity)  
  - LDR (Light Detection)  
  - IR Sensor (Motion Detection)  
- **Cloud Platform:** ThingSpeak  
- **Libraries:** RPi.GPIO, adafruit_dht, requests  

---

## System Workflow
1. Sensors collect environmental data  
2. Raspberry Pi processes the data  
3. Alerts are triggered if thresholds are exceeded  
4. Data is stored locally in a CSV file  
5. Periodically, data is sent to ThingSpeak cloud  

---

## How to Run the Project
1. Install required dependencies:
   ```bash
   pip install adafruit-circuitpython-dht requests
