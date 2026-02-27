import requests
import json
import time

print("===== GOD MODE AI HUNTER QUANTUM v8 STARTED =====")

# OUTFITTERS JSON API
URL = "https://outfitters.com.pk/products.json?limit=250"

# ntfy topic (YOU SUBSCRIBED THIS)
NTFY_TOPIC = "outfitters-amin"

STATE_FILE = "state.json"


# LOAD OLD PRICES
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
            headers={"Title": title}
        )
        print("Push sent")

    except Exception as e:
        print("Push Error:", e)


# GET PRODUCTS
def get_products():

    products = []

    r = requests.get(URL, timeout=30)

    data = r.json()

    for p in data["products"]:

        title = p["title"]

        handle = p["handle"]

        for v in p["variants"]:

            price = float(v["price"])

            product_url = f"https://outfitters.com.pk/products/{handle}"

            products.append({
                "title": title,
                "price": price,
                "url": product_url
            })

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

    if key not in old_prices:

        send_push(
            "🆕 New Product",
            f"{title}\nPrice: PKR {price}\n{url}"
        )

        alerts += 1

        print("NEW:", title)

    else:

        old_price = old_prices[key]

        if price != old_price:

            diff = price - old_price

            percent = (diff / old_price) * 100

            send_push(
                "💰 Price Changed",
                f"{title}\nOld: PKR {old_price}\nNew: PKR {price}\nChange: {round(percent,2)}%\n{url}"
            )

            alerts += 1

            print("PRICE CHANGE:", title)


# SAVE STATE
with open(STATE_FILE, "w") as f:
    json.dump(new_prices, f)


print("Alerts sent:", alerts)

print("Scan complete.")
