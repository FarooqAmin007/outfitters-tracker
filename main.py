import requests
import time

print("===== GOD TRACKER STARTED =====")

# ===== PUSHBULLET TOKEN =====

PUSH_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"


# ===== PRODUCTS (Shopify JSON Links) =====

products = {

"Puffer Jacket":
"https://outfitters.com.pk/products/quilted-puffer-jacket-with-hood-1.js",

}


# ===== STORE LAST PRICES =====

last_prices = {}


# ===== PUSH FUNCTION =====

def send_push(title,message):

    requests.post(
        "https://api.pushbullet.com/v2/pushes",
        headers={
            "Access-Token": PUSH_TOKEN,
            "Content-Type":"application/json"
        },
        json={
            "type":"note",
            "title":title,
            "body":message
        }
    )

    print("Push Sent")



# ===== GET PRICE FROM SHOPIFY =====

def get_price(url):

    try:

        r = requests.get(url,timeout=20)

        data = r.json()

        variant = data["variants"][0]

        price = int(variant["price"]) / 100

        return int(price)

    except Exception as e:

        print("Price error:",e)

        return None



# ===== MAIN LOOP =====

while True:

    print("Checking products...")

    for name,url in products.items():

        price = get_price(url)

        if price is None:

            print(name,"Price error")
            continue


        print(name,"=",price)

        old_price = last_prices.get(name)


        # FIRST TIME SAVE
        if old_price is None:

            last_prices[name] = price

            print("First price saved")

            continue


        # PRICE CHANGE ALERT
        if price != old_price:

            if price < old_price:

                change="📉 Price Dropped"

            else:

                change="📈 Price Increased"


            send_push(

            "🔥 Outfitters Price Change",

            f"{name}\n\n"
            f"Old Price: PKR {old_price}\n"
            f"New Price: PKR {price}\n\n"
            f"{change}"

            )


            last_prices[name] = price


        else:

            print("No change")


    print("Waiting 5 minutes...\n")

    time.sleep(300)