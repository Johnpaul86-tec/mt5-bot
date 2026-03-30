import time
import requests
from mt5_utils import connect, place_trade

SERVER_URL = "http://127.0.0.1:5000"

login = int(input("MT5 Login: "))
password = input("Password: ")
server = input("Server: ")

connect(login, password, server)

LOT = 0.01
SL = 50
TP = 100

while True:
    try:
        status = requests.get(f"{SERVER_URL}/api/bot_status").json()

        if status["running"]:
            signal = requests.get(f"{SERVER_URL}/api/signal").json()["signal"]

            if signal in ["BUY", "SELL"]:
                place_trade("EURUSD", signal, LOT, SL, TP)

        time.sleep(5)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
