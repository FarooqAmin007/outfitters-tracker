import requests
import json
import time
import os

print("===== GOD MODE AI HUNTER QUANTUM v7 STARTED =====")


########################################
# PUSHBULLET SETTINGS
########################################

PUSH_TOKEN = "o.lzUjCYd51OeBnWCqPHZYmDaiMkx38BwG"


def send_push(title, message):

    try:

        r = requests.post(
            "https://api.pushbullet.com/v2/pushes",
            headers={
                "Access-Token": PUSH_TOKEN,
                "Content-Type": "application/json"
            },
            json={
                "type": "note",
                "title": title,
                "body": message
            }
        )

        print("Pushbullet:", r.status_code)

    except Exception as e:
        print("Push Error:", e)


########################################
# MEMORY SYSTEM
########################################

STATE_FILE = "state.json"


def load_state():

    if os.path.exists(STATE_FILE):

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    return {}


def save_state(data):

    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


memory = load_state()


########################################
# OUTFITTERS API
########################################

URL = "https://outfitters.com.pk/products.json?limit=250"


print("Scanning Outfitters realtime...")


try:

    r = requests.get(URL, timeout=20)

    data = r.json()

    products = data["products"]

    print("Products found:", len(products))


    alerts = 0


    for product in products:

        name = product["title"]

        handle = product["handle"]

        link = "https://outfitters.com.pk/products/" + handle


        variant = product["variants"][0]

        price = float(variant["price"])


        key = name


        #################################
        # NEW PRODUCT
        #################################

        if key not in memory:

            memory[key] = price

            print("NEW:", name)

            send_push(
                "🆕 New Product",
                f"{name}\nPrice: {price} PKR\n{link}"
            )

            alerts += 1


        #################################
        # PRICE CHANGE
        #################################

        else:

            old_price = memory[key]

            if price != old_price:

                diff = price - old_price

                percent = (diff / old_price) * 100

                memory[key] = price

                print("PRICE CHANGE:", name)

                send_push(
                    "💰 Price Changed",
                    f"{name}\nOld: {old_price} PKR\nNew: {price} PKR\nChange: {percent:.1f}%\n{link}"
                )

                alerts += 1


    print("Alerts sent:", alerts)


    save_state(memory)


except Exception as e:

    print("ERROR:", e)


print("Scan complete.")

