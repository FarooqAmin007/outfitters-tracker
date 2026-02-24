import requests
import time
import re

# ===== SETTINGS =====

URL = "https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1.js"

PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

CHECK_INTERVAL = 300  # 5 minutes

last_price = None


# ===== PUSH FUNCTION =====

def send_push(message):

    requests.post(
        "https://api.pushbullet.com/v2/pushes",
        json={
            "type": "note",
            "title": "Outfitters Price Alert",
            "body": message
        },
        headers={
            "Access-Token": PUSHBULLET_TOKEN
        }
    )


# ===== GET PRICE FUNCTION =====

def get_price():

    r = requests.get(URL)

    data = r.json()

    price_paisa = data["variants"][0]["price"]

    price = price_paisa / 100

    return f"PKR {int(price)}"


# ===== MAIN LOOP =====

print("===== OUTFITTERS TRACKER STARTED =====")

while True:

    print("Fetching price...")

    try:

        price = get_price()

        print("Price:", price)

        global last_price

        if price != last_price:

            send_push(f"Price Update: {price}")

            print("Push sent!")

            last_price = price

    except Exception as e:

        print("Error:", e)

    time.sleep(CHECK_INTERVAL)