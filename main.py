import requests
import time
import json
from bs4 import BeautifulSoup

print("===== GOD TRACKER AI SUPREME JSON ENGINE STARTED =====")

# SETTINGS

PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

BASE_URL = "https://outfitters.com.pk/collections/all"

CHECK_INTERVAL = 600

PRICE_FILE = "prices.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# LOAD SAVED PRICES

try:
    with open(PRICE_FILE,"r") as f:
        saved_prices = json.load(f)
except:
    saved_prices = {}


# PUSH NOTIFICATION

def push(title,message,link):

    try:

        requests.post(
            "https://api.pushbullet.com/v2/pushes",
            headers={"Access-Token":PUSHBULLET_TOKEN},
            json={
                "type":"link",
                "title":title,
                "body":message,
                "url":link
            },
            timeout=20
        )

        print("Push sent")

    except Exception as e:

        print("Push error:",e)


# GET PRICE FROM SHOPIFY JSON

def get_price(product_url):

    try:

        json_url = product_url.split("?")[0] + ".json"

        r = requests.get(json_url,headers=HEADERS,timeout=20)

        data = r.json()

        price = data["product"]["variants"][0]["price"]

        return int(float(price))

    except Exception as e:

        print("Price error:",e)

        return None


# SCAN PRODUCTS

def scan_products():

    print("Scanning Outfitters AI SUPREME...")

    products=[]

    try:

        r=requests.get(BASE_URL,headers=HEADERS,timeout=20)

        soup=BeautifulSoup(r.text,"html.parser")

        links=soup.find_all("a",href=True)

        for link in links:

            href=link["href"]

            if "/products/" in href:

                url="https://outfitters.com.pk"+href

                name=link.text.strip()

                if len(name)>3:

                    products.append((name,url))


        products=list(set(products))


    except Exception as e:

        print("Scan error:",e)

    return products


# MAIN LOOP

while True:

    print("\nChecking products...")

    products=scan_products()

    print("Products Found:",len(products))


    for name,url in products:

        price=get_price(url)

        if price is None:
            continue

        print(name,"=",price)

        old_price=saved_prices.get(url)


        # FIRST SAVE

        if old_price is None:

            saved_prices[url]=price

            continue


        # PRICE CHANGE

        if price!=old_price:


            diff=price-old_price


            if diff<0:
                direction="⬇ PRICE DROP"
            else:
                direction="⬆ PRICE INCREASE"


            message=f"""

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

            saved_prices[url]=price


    with open(PRICE_FILE,"w") as f:

        json.dump(saved_prices,f)


    print("Sleeping",CHECK_INTERVAL,"seconds")

    time.sleep(CHECK_INTERVAL)