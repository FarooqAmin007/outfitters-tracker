import requests
import time
import json
from bs4 import BeautifulSoup

print("===== GOD TRACKER AI SUPREME v3 STARTED =====")


# SETTINGS

PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

BASE_COLLECTION = "https://outfitters.com.pk/collections/all?page="

CHECK_INTERVAL = 900   # 15 minutes

MAX_PAGES = 50   # scans up to 50 pages (~1000+ products)

PRICE_FILE = "prices.json"


HEADERS = {
    "User-Agent":"Mozilla/5.0"
}


# LOAD PRICES

try:
    with open(PRICE_FILE,"r") as f:
        saved_prices=json.load(f)
except:
    saved_prices={}



# PUSH ALERT

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



# SHOPIFY PRICE ENGINE

def get_price(url):

    try:

        json_url=url.split("?")[0]+".json"

        r=requests.get(json_url,headers=HEADERS,timeout=20)

        data=r.json()

        variant=data["product"]["variants"][0]

        price=int(float(variant["price"]))

        compare=variant["compare_at_price"]

        if compare:

            compare=int(float(compare))

        return price,compare

    except Exception as e:

        print("Price error:",e)

        return None,None



# SCAN ALL PAGES

def scan_all_products():

    print("Scanning FULL Outfitters Website...")

    products=[]

    for page in range(1,MAX_PAGES+1):

        try:

            url=BASE_COLLECTION+str(page)

            r=requests.get(url,headers=HEADERS,timeout=20)

            soup=BeautifulSoup(r.text,"html.parser")

            links=soup.find_all("a",href=True)

            for link in links:

                href=link["href"]

                if "/products/" in href:

                    name=link.text.strip()

                    if len(name)>3:

                        full="https://outfitters.com.pk"+href

                        products.append((name,full))

            print("Page",page,"scanned")

        except:

            pass


    products=list(set(products))

    return products



# MAIN LOOP

while True:

    print("\nScanning products...")

    products=scan_all_products()

    print("TOTAL PRODUCTS:",len(products))


    for name,url in products:

        price,compare=get_price(url)

        if price is None:
            continue

        print(name,"=",price)

        old=saved_prices.get(url)


        # FIRST SAVE

        if old is None:

            saved_prices[url]=price

            continue


        # PRICE CHANGE

        if price!=old:

            diff=price-old


            if diff<0:
                direction="⬇ PRICE DROP"
            else:
                direction="⬆ PRICE INCREASE"


            message=f"""

{name}

{direction}

Old Price: PKR {old}
New Price: PKR {price}

Product Link:
{url}

"""

            push(
                "🔥 Outfitters Price Alert",
                message,
                url
            )


            saved_prices[url]=price


        # BIG DISCOUNT ALERT

        if compare:

            discount=int((compare-price)/compare*100)

            if discount>=70:

                message=f"""

{name}

🔥 HUGE DISCOUNT {discount}%

Old Price: PKR {compare}
Sale Price: PKR {price}

Product Link:
{url}

"""

                push(
                    "🔥 70%+ SALE DETECTED",
                    message,
                    url
                )


    with open(PRICE_FILE,"w") as f:

        json.dump(saved_prices,f)


    print("Sleeping",CHECK_INTERVAL,"seconds")

    time.sleep(CHECK_INTERVAL)