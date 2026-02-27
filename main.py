import requests
import json

print("===== GOD MODE AI HUNTER QUANTUM v8.1 STARTED =====")

URL = "https://outfitters.com.pk/products.json?limit=250"

NTFY_TOPIC = "outfitters-amin"

STATE_FILE = "state.json"


# LOAD OLD DATA
try:
    with open(STATE_FILE, "r") as f:
        old_prices = json.load(f)
except:
    old_prices = {}


# SEND ntfy PUSH
def send_push(title, message):

    try:

        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": title.encode("ascii", "ignore").decode()
            }
        )

        print("Push sent")

    except Exception as e:

        print("Push Error:", e)


# GET PRODUCTS
def get_products():

    products = []

    page = 1

    while True:

        r = requests.get(
            f"https://outfitters.com.pk/products.json?limit=250&page={page}",
            timeout=30
        )

        data = r.json()

        if not data["products"]:
            break

        for p in data["products"]:

            title = p["title"]

            handle = p["handle"]

            for v in p["variants"]:

                price = float(v["price"])

                url = f"https://outfitters.com.pk/products/{handle}"

                products.append({
                    "title": title,
                    "price": price,
                    "url": url
                })

        page += 1

    return products


print("Scanning Outfitters realtime...")

products = get_products()

print("Products found:", len(products))


new_prices = {}

alerts = 0


for p in products:

    title = p["title"]
    price = p["price"]
    url = p["url"]

    key = title

    new_prices[key] = price


    # NEW PRODUCT
    if key not in old_prices:

        send_push(
            "New Product",
            f"""🆕 NEW PRODUCT

{title}

Price: PKR {price}

{url}
"""
        )

        print("NEW:", title)

        alerts += 1


    # PRICE CHANGE
    else:

        old_price = old_prices[key]

        if price != old_price:

            diff = price - old_price

            percent = (diff / old_price) * 100

            send_push(
                "Price Changed",
                f"""💰 PRICE CHANGE

{title}

Old Price: PKR {old_price}
New Price: PKR {price}

Change: {round(percent,2)} %

{url}
"""
            )

            print("PRICE CHANGE:", title)

            alerts += 1


# SAVE MEMORY
with open(STATE_FILE, "w") as f:
    json.dump(new_prices, f)


print("Alerts sent:", alerts)

print("Scan complete.")
