import requests
from bs4 import BeautifulSoup
import time
import re

print("===== ULTRA TRACKER V2 STARTED =====")

# ===== PUSHBULLET TOKEN =====

PUSH_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

# ===== PRODUCTS =====

products = {

"Puffer Jacket":
"https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1?variant=44728895373503",

}

# ===== STORE LAST PRICES =====

last_prices = {}

# ===== PUSH FUNCTION =====

def send_push(title,message):

    requests.post(
        "https://api.pushbullet.com/v2/pushes",
        headers={
            "Access-Token": PUSH_TOKEN,
            "Content-Type": "application/json"
        },
        json={
            "type":"note",
            "title":title,
            "body":message
        }
    )

    print("Push Sent")


# ===== GET PRICE FUNCTION =====

def get_price(url):

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    r = requests.get(url,headers=headers)

    soup = BeautifulSoup(r.text,"html.parser")

    text = soup.get_text()

    match = re.search(r'PKR\s*([0-9,]+)',text)

    if match:

        price = int(match.group(1).replace(",",""))

        return price

    return None


# ===== MAIN LOOP =====

while True:

    print("Checking products...")

    for name,url in products.items():

        price = get_price(url)

        if price is None:

            print(name,"Price not found")
            continue

        print(name,"=",price)

        old_price = last_prices.get(name)

        # First time only save
        if old_price is None:

            last_prices[name] = price
            print("First price saved")

            continue


        # PRICE CHANGE ALERT
        if price != old_price:

            if price < old_price:
                change_type = "📉 Price Dropped"
            else:
                change_type = "📈 Price Increased"


            send_push(

            "🔥 Outfitters Price Change",

            f"{name}\n\n"
            f"Old Price: PKR {old_price}\n"
            f"New Price: PKR {price}\n\n"
            f"{change_type}\n\n"
            f"{url}"

            )

            last_prices[name] = price

        else:

            print("No change")


    print("Waiting 5 minutes...\n")

    time.sleep(300)