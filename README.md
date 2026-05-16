# IOT-Based-Flood-Monitoring-Alert-and-Control-System

## Overview

This project monitors rainfall and water level continuously using an ultrasonic sensor and a rain sensor connected to an ESP32. The data is sent to a Flask backend, analyzed using a weighted risk-score algorithm, and displayed on a live dashboard with charts and a map.

When the system detects warning or danger conditions, it can send email alerts and switch a relay to control a water pump. The goal is to reduce manual monitoring and respond faster in flood-prone areas.

## Features

- Real-time water level and rainfall monitoring using ESP32.
- Risk scoring based on water proximity, rainfall intensity, and atmospheric pressure.
- Automatic pump control through a relay module.
- Live dashboard with charts and map view.
- SMTP email alerts for warning and danger states.
- State-based alerting to avoid duplicate emails during sustained risk conditions.

## Setup

### Hardware
- ESP32
- Ultrasonic sensor
- Rain sensor
- Relay module
- Water pump
- Jumper wires and power supply

### Software
- Python 3.7+
- Flask
- Arduino IDE
- HTML/CSS/JavaScript

### Run the Project
1. Clone the repository.
2. Install the Python dependencies.
3. Upload the ESP32 code using Arduino IDE.
4. Update the Wi-Fi, server, and API credentials.
5. Start the Flask server.
6. Open the dashboard in your browser.

## How It Works

1. ESP32 reads water level and rain sensor values.
2. Sensor data is sent to the Flask server over HTTP POST.
3. The server combines sensor readings with weather data to compute a flood risk score.
4. The dashboard updates live with charts, status indicators, and map data.
5. If the risk crosses a threshold, the relay activates the pump and an email alert is sent.

## Flood Risk Score Formula
 
```
Risk Score = (0.5 × Water Factor) + (0.3 × Rain Factor) + (0.2 × Pressure Factor)
```

