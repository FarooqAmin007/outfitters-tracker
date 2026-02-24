import requests
from bs4 import BeautifulSoup
import time

# ========= SETTINGS =========

URL = "https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1?variant=44728895373503"

PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

CHECK_INTERVAL = 600   # 10 minutes

last_price = None


# ========= PUSH NOTIFICATION =========

def send_push(title, message):

    print("Sending Pushbullet notification...")

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


# ========= PRICE SCRAPER =========

def get_price():

    print("Fetching price...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.text

    import re

    match = re.search(r'Rs\.\s?([\d,]+)', text)

    if match:
        price = float(match.group(1).replace(",", ""))
        return price

    return None


# ========= MAIN LOOP =========

print("===== OUTFITTERS TRACKER STARTED =====")

while True:

    price = get_price()

    if price:

        print("Current Price:", price)

        global last_price

        if last_price is None:

            last_price = price

            send_push(
                "Tracker Started",
                f"Monitoring price: Rs {price}"
            )

        elif price != last_price:

            send_push(
                "🔥 Price Changed!",
                f"Old Price: Rs {last_price}\nNew Price: Rs {price}\n{URL}"
            )

            last_price = price

    else:

        print("Price not found")

    time.sleep(CHECK_INTERVAL)