import requests
import json
import time

print("===== GOD MODE AI HUNTER QUANTUM v9 HYPER ENGINE STARTED =====")

# PUSH SERVICE
PUSH_URL = "https://ntfy.sh/outfitters-amin"

# SHOPIFY API
BASE = "https://outfitters.com.pk/products.json?limit=250&page="

STATE_FILE = "state.json"

# LOAD MEMORY
try:
    with open(STATE_FILE, "r") as f:
        old_state = json.load(f)
except:
    old_state = {}

new_state = {}

alerts = 0
page = 1
total_products = 0


# PUSH FUNCTION
def send_push(title, msg):

    try:

        requests.post(
            PUSH_URL,
            data=f"{title}\n{msg}".encode("utf-8"),
            timeout=10
        )

        print("Push sent")

    except Exception as e:
        print("Push error:", e)


print("Scanning Outfitters HYPER mode...")

while True:

    try:

        r = requests.get(BASE + str(page), timeout=20)

        data = r.json()

        products = data["products"]

        if not products:
            break

        for p in products:

            title = p["title"]

            handle = p["handle"]

            link = f"https://outfitters.com.pk/products/{handle}"

            variant = p["variants"][0]

            price = float(variant["price"])

            compare = variant["compare_at_price"]

            if compare:
                compare = float(compare)
            else:
                compare = price


            key = handle

            new_state[key] = price

            total_products += 1


            # NEW PRODUCT
            if key not in old_state:

                alerts += 1

                send_push(
                    "NEW PRODUCT",
                    f"{title}\nPKR {price}\n{link}"
                )

                print("NEW:", title)

            else:

                old_price = old_state[key]

                # PRICE CHANGE
                if price != old_price:

                    alerts += 1

                    send_push(
                        "PRICE CHANGE",
                        f"{title}\nPKR {old_price} → PKR {price}\n{link}"
                    )

                    print("PRICE CHANGE:", title)


        page += 1

        time.sleep(0.5)

    except Exception as e:

        print("Scan error:", e)

        break


# REMOVED PRODUCTS
for key in old_state:

    if key not in new_state:

        alerts += 1

        send_push(
            "REMOVED PRODUCT",
            key
        )

        print("REMOVED:", key)


# SAVE MEMORY
with open(STATE_FILE, "w") as f:

    json.dump(new_state, f)


print("Products scanned:", total_products)
print("Alerts sent:", alerts)
print("Scan complete.")
