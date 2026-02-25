import requests
import time
import random
import json

print("===== GOD MODE AI HUNTER QUANTUM v4 STARTED =====")

# ---------- SETTINGS ----------

MAX_PRODUCTS = 500
DELAY = 1.5
LOW_LOG_MODE = True

SHOPIFY_SITES = [
    "https://gymshark.com",
    "https://allbirds.com",
    "https://ridge.com",
    "https://mvmt.com",
    "https://colourpop.com"
]

# ---------- SAFE PRICE PARSER ----------

def parse_price(value):
    try:
        return float(str(value).replace(",", "").replace("$",""))
    except:
        return 0.0


# ---------- GET PRODUCTS ----------

def get_products(site):

    try:

        url = site + "/products.json?limit=250"

        r = requests.get(url, timeout=15)

        data = r.json()

        products = data.get("products", [])

        return products

    except Exception as e:

        if not LOW_LOG_MODE:
            print("Error:", site, e)

        return []


# ---------- SCANNER ----------

def scan_site(site):

    products = get_products(site)

    print(f"Scanning {site}")

    print("Products found:", len(products))

    for p in products[:MAX_PRODUCTS]:

        try:

            title = p["title"]

            variant = p["variants"][0]

            price = parse_price(variant["price"])

            compare = parse_price(variant.get("compare_at_price"))

            discount = 0

            if compare > 0:

                discount = round((compare-price)/compare*100,1)

            if discount > 40:

                print("🔥 DEAL FOUND")

                print(title)

                print("Price:", price)

                print("Was:", compare)

                print("Discount:", discount,"%")

                print("------")

        except:
            pass


# ---------- MAIN LOOP ----------

def main():

    total = 0

    for site in SHOPIFY_SITES:

        scan_site(site)

        total += 1

        time.sleep(DELAY)

    print("Scan Complete")

main()
