import requests
from bs4 import BeautifulSoup
import time
import re

print("===== OUTFITTERS TRACKER STARTED =====")

# PRODUCT URL
URL = "https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1?variant=44728895373503"

# PUSHBULLET TOKEN
PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

CHECK_INTERVAL = 600  # 10 minutes

last_price = None


# PUSH NOTIFICATION
def send_push(title, message):

    print("Sending notification...")

    data = {
        "type": "note",
        "title": title,
        "body": message
    }

    headers = {
        "Access-Token": PUSHBULLET_TOKEN,
        "Content-Type": "application/json"
    }

    requests.post(
        "https://api.pushbullet.com/v2/pushes",
        json=data,
        headers=headers
    )


# GET PRICE
def get_price():

    print("Fetching price...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.text

    match = re.search(r'PKR\s*(\d+)', text)

    if match:
        return float(match.group(1))

    return None


# MAIN LOOP

while True:

    price = get_price()

    if price:

        print("Current Price:", price)

        if last_price is None:

            last_price = price

            send_push(
                "Tracker Started",
                f"Monitoring price Rs {price}"
            )

        elif price != last_price:

            send_push(
                "🔥 Price Changed",
                f"Old Price Rs {last_price}\nNew Price Rs {price}"
            )

            last_price = price

    else:

        print("Price not found")

    time.sleep(CHECK_INTERVAL)