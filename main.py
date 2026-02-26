import requests
import json
import os

print("===== GOD MODE AI HUNTER QUANTUM v6 ULTRA STARTED =====")

# =============================
# SETTINGS
# =============================

SITE = "https://outfitters.com.pk"
API = SITE + "/products.json?limit=250"

PUSH_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

STATE_FILE = "state.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# =============================
# PUSHBULLET
# =============================

def push(title, message):

    try:

        requests.post(
            "https://api.pushbullet.com/v2/pushes",
            headers={"Access-Token": PUSH_TOKEN},
            json={
                "type": "note",
                "title": title,
                "body": message
            }
        )

        print("Push sent:", title)

    except Exception as e:

        print("Push error")


# =============================
# LOAD / SAVE STATE
# =============================

def load_state():

    if os.path.exists(STATE_FILE):

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    return {}


def save_state(state):

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# =============================
# SCAN PRODUCTS
# =============================

def scan():

    print("Scanning Outfitters...")

    state = load_state()
    new_state = {}

    try:

        r = requests.get(API, headers=HEADERS, timeout=20)
        data = r.json()

    except:

        print("API error")
        return

    products = data.get("products", [])

    print("Products found:", len(products))

    for product in products:

        title = product["title"]
        handle = product["handle"]
        link = SITE + "/products/" + handle

        for variant in product["variants"]:

            variant_id = str(variant["id"])

            price = float(variant["price"])
            compare = float(variant["compare_at_price"] or 0)

            key = variant_id

            new_state[key] = {
                "title": title,
                "price": price,
                "compare": compare,
                "link": link
            }

            if key not in state:
                continue

            old_price = state[key]["price"]
            old_compare = state[key]["compare"]

            # ANY PRICE CHANGE (UP OR DOWN)
            if price != old_price:

                message = f"""
{title}

Old Price: Rs {int(old_price)}
New Price: Rs {int(price)}

{link}
"""

                push("PRICE CHANGED", message)


            # ANY DISCOUNT CHANGE
            if compare != old_compare:

                if compare > 0:

                    discount = int((compare - price) / compare * 100)

                    message = f"""
{title}

New Discount: {discount}%

Price: Rs {int(price)}
Was: Rs {int(compare)}

{link}
"""

                    push("DISCOUNT UPDATED", message)


    save_state(new_state)

    print("Scan complete.")


# RUN ONCE (GitHub runs every 5 minutes)
scan()
