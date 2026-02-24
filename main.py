import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin

# =========================
# SETTINGS
# =========================

BASE_URL = "https://outfitters.com.pk"

SCAN_DELAY = 600   # 10 minutes

MAX_PRODUCTS = 10000

PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"


# =========================
# DATABASE FILE
# =========================

DB_FILE = "prices.json"


# =========================
# PUSHBULLET ALERT
# =========================

def push_alert(title, message):

    try:

        requests.post(
            "https://api.pushbullet.com/v2/pushes",
            headers={"Access-Token": PUSHBULLET_TOKEN},
            json={
                "type": "note",
                "title": title,
                "body": message
            }
        )

        print("Push sent!")

    except:

        print("Push failed")


# =========================
# LOAD PRICES
# =========================

def load_prices():

    try:
        with open(DB_FILE,"r") as f:
            return json.load(f)
    except:
        return {}


# =========================
# SAVE PRICES
# =========================

def save_prices(data):

    with open(DB_FILE,"w") as f:
        json.dump(data,f)


# =========================
# GET PRICE
# =========================

def get_price(soup):

    text = soup.get_text()

    import re

    match = re.search(r'PKR\s?([0-9,]+)', text)

    if match:

        return int(match.group(1).replace(",",""))

    return None


# =========================
# GET NAME
# =========================

def get_name(soup):

    title = soup.find("title")

    if title:
        return title.text.strip()

    return "Product"


# =========================
# SCAN PRODUCT
# =========================

def scan_product(url,prices):

    try:

        r = requests.get(url,timeout=15)

        soup = BeautifulSoup(r.text,"html.parser")

        price = get_price(soup)

        if price is None:
            return

        name = get_name(soup)

        old_price = prices.get(url)

        print(name,"=",price)

        # First time save
        if old_price is None:

            prices[url] = price

            print("First price saved")

            return


        # Price changed
        if price != old_price:

            change = price - old_price

            if change > 0:
                direction = "INCREASED"
            else:
                direction = "DECREASED"


            message = f"""

{name}

Old Price: {old_price}

New Price: {price}

Price {direction}

{url}

"""

            push_alert("PRICE CHANGE", message)

            prices[url] = price

    except:

        print("Error scanning",url)



# =========================
# SCAN WEBSITE
# =========================

def scan_site():

    print("Scanning Outfitters...")

    try:

        r = requests.get(BASE_URL)

        soup = BeautifulSoup(r.text,"html.parser")

        links = soup.find_all("a")

        products = []

        for link in links:

            href = link.get("href")

            if href:

                full = urljoin(BASE_URL,href)

                if "/products/" in full:

                    products.append(full)

        return list(set(products))[:MAX_PRODUCTS]

    except:

        return []



# =========================
# MAIN LOOP
# =========================

print("===== GOD TRACKER PUSHBULLET STARTED =====")

prices = load_prices()

while True:

    products = scan_site()

    print("Products Found:",len(products))

    for p in products:

        scan_product(p,prices)

    save_prices(prices)

    print("Waiting",SCAN_DELAY,"seconds")

    time.sleep(SCAN_DELAY)