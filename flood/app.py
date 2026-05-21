from flask import Flask, render_template, jsonify, request
import requests
import smtplib
import pandas as pd
from email.mime.text import MIMEText

app = Flask(__name__)

# ===== GLOBAL SENSOR VALUES =====
rain_sensor = 0
water_distance = 0
last_risk_status = "SAFE"
email_status = "No Alert"

# ===== OPENWEATHER API =====
API_KEY = "YOUR_API_KEY"

LAT = Enter Latitude
LON = Enter Longitude


# ===== WEATHER DATA =====
def get_weather():

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]

    rainfall = 0
    if "rain" in data:
        rainfall = data["rain"].get("1h", 0)

    return temperature, humidity, pressure, rainfall


# ===== RECEIVE ESP32 SENSOR DATA =====
@app.route("/sensor", methods=["POST"])
def receive_sensor():

    global rain_sensor, water_distance

    data = request.json

    rain_sensor = data["rain"]
    water_distance = data["water"]

    print("ESP32 DATA:", rain_sensor, water_distance)

    temperature, humidity, pressure, rainfall = get_weather()

    return jsonify({
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "rainfall": rainfall
    })


# ===== EMAIL FUNCTION =====
def send_email(subject, message):

    sender = "abinayaprabu0602@gmail.com"
    password = "vagrngmngqyixerr"
    receiver = "abinaya2310921@ssn.edu.in"

    msg = MIMEText(message)

    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        print("Email Sent")

    except Exception as e:
        print(e)


# ===== DASHBOARD ROUTES =====
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/weather")
def weather_dashboard():
    return render_template("weather_dashboard.html")


# ===== DASHBOARD DATA =====
@app.route("/data")
def get_data():

    global last_risk_status, email_status

    current_time = pd.Timestamp.now().strftime("%H:%M:%S")

    temp, humidity, pressure, rainfall_api = get_weather()

    rainfall = rain_sensor

    if rain_sensor < 2000:
        rain_status = "RAIN DETECTED"
    else:
        rain_status = "NO RAIN"

    distance = round(water_distance, 2)

    # ===== FLOOD RISK SCORE =====
    if distance <= 10:
        water_factor = 100
    elif distance <= 20:
        water_factor = 60
    else:
        water_factor = 20

    if rain_sensor < 2000:
        rain_factor = 80
    else:
        rain_factor = 10

    pressure_factor = (1015 - pressure) * 5

    if pressure_factor < 0:
        pressure_factor = 0

    if pressure_factor > 100:
        pressure_factor = 100

    risk_score = round(
        0.5 * water_factor +
        0.3 * rain_factor +
        0.2 * pressure_factor,
        2
    )

    # ===== RISK LEVEL =====
    if risk_score >= 70:
        risk = "DANGER"
    elif risk_score > 40:
        risk = "WARNING"
    else:
        risk = "SAFE"

    # ===== MOTOR =====
    if risk == "DANGER":
        motor = "ON"
    else:
        motor = "OFF"

    # ===== EMAIL ALERT =====
    # ===== EMAIL ALERT =====

    if risk == "WARNING" and last_risk_status != "WARNING":
        send_email(
            "Flood Warning",
            f"Water Level: {distance} cm\nTemperature: {temp}\nPressure: {pressure}"
        )
        email_status = "Warning Email Sent"

    elif risk == "DANGER" and last_risk_status != "DANGER":
        send_email(
            "Flood Danger",
            f"Water Level: {distance} cm\nTemperature: {temp}\nPressure: {pressure}"
        )
        email_status = "Danger Email Sent"

    elif risk == "WARNING":
        email_status = "Warning Active"

    elif risk == "DANGER":
        email_status = "Danger Active"

    else:
        email_status = "No Alert"
    
    last_risk_status = risk

    return jsonify({

        "rainfall": rainfall,
        "rain_status": rain_status,
        "water": distance,
        "risk": risk,
        "risk_score": risk_score,
        "motor": motor,
        "email_status": email_status,
        "time": current_time,
        "temperature": temp,
        "humidity": humidity,
        "pressure": pressure

    })


# ===== RUN SERVER =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
