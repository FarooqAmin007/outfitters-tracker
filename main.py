import requests
from bs4 import BeautifulSoup
import time

# ===== SETTINGS =====

URL = "https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1?variant=44728895373503"

PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

CHECK_INTERVAL = 300   # 5 minutes

last_price = None

# ===== FUNCTIONS =====

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


def get_price():

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    r = requests.get(URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text()

    import re

    match = re.search(r'PKR\s*[\d,]+', text)

    if match:
        return match.group()

    return None


# ===== MAIN LOOP =====

print("===== OUTFITTERS TRACKER STARTED =====")

while True:

    print("Fetching price...")

    price = get_price()

    if price:

        print("Price:", price)

        if price != last_price:

            message = f"Price Update: {price}\n{URL}"

            send_push(message)

            print("Push sent!")

            last_price = price

    else:
        print("Price not found")

    time.sleep(CHECK_INTERVAL)