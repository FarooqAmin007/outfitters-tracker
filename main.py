import requests
import time
import json
import re
from bs4 import BeautifulSoup

print("===== GOD TRACKER AI SUPREME FINAL STARTED =====")

# ========= SETTINGS =========

PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

BASE_URL = "https://outfitters.com.pk/collections/all"

CHECK_INTERVAL = 600   # 10 minutes

PRICE_FILE = "prices.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ========= LOAD OLD PRICES =========

try:
    with open(PRICE_FILE, "r") as f:
        saved_prices = json.load(f)
except:
    saved_prices = {}

# ========= PUSH NOTIFICATION =========

def push(title, message, link):

    try:
        requests.post(
            "https://api.pushbullet.com/v2/pushes",
            headers={
                "Access-Token": PUSHBULLET_TOKEN
            },
            json={
                "type": "link",
                "title": title,
                "body": message,
                "url": link
            },
            timeout=20
        )

        print("Push sent")

    except Exception as e:
        print("Push error:", e)


# ========= EXTRACT PRICE =========

def extract_price(text):

    match = re.search(r'(\d[\d,]*)', text)

    if match:
        return int(match.group(1).replace(",", ""))

    return None


# ========= GET PRODUCT PRICE =========

def get_price(url):

    try:

        r = requests.get(url, headers=HEADERS, timeout=20)

        soup = BeautifulSoup(r.text, "html.parser")

        text = soup.get_text()

        price = extract_price(text)

        return price

    except Exception as e:

        print("Error:", e)

        return None


# ========= SCAN WEBSITE =========

def scan_products():

    print("Scanning Outfitters AI SUPREME...")

    products = []

    try:

        r = requests.get(BASE_URL, headers=HEADERS, timeout=20)

        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.find_all("a", href=True)

        for link in links:

            href = link["href"]

            if "/products/" in href:

                url = "https://outfitters.com.pk" + href

                name = link.text.strip()

                if len(name) > 2:

                    products.append((name, url))

        products = list(set(products))

    except Exception as e:

        print("Scan error:", e)

    return products


# ========= MAIN LOOP =========

while True:

    print("\nChecking products...")

    products = scan_products()

    print("Products Found:", len(products))

    for name, url in products:

        price = get_price(url)

        if price is None:
            continue

        print(name, "=", price)

        old_price = saved_prices.get(url)

        # FIRST SAVE
        if old_price is None:

            saved_prices[url] = price

            continue

        # PRICE CHANGE
        if price != old_price:

            diff = price - old_price

            if diff < 0:
                direction = "⬇ PRICE DROP"
            else:
                direction = "⬆ PRICE INCREASE"

            message = f"""
{name}

Old Price: PKR {old_price}
New Price: PKR {price}

Change: {diff} PKR

Open Product:
{url}
"""

            push(
                "🔥 Outfitters Price Change",
                message,
                url
            )

            saved_prices[url] = price


    # SAVE DATABASE

    with open(PRICE_FILE, "w") as f:

        json.dump(saved_prices, f)


    print("Sleeping", CHECK_INTERVAL, "sec...")

    time.sleep(CHECK_INTERVAL)