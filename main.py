import requests
import time
import json
from bs4 import BeautifulSoup

print("===== GOD TRACKER AI SUPREME v4 STARTED =====")


#########################################
# SETTINGS
#########################################

PUSH_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

BASE = "https://outfitters.com.pk/collections/all?page="

MAX_PAGES = 80     # scans thousands products

CHECK_INTERVAL = 600   # 10 minutes

PRICE_FILE="prices.json"

HEADERS={
"User-Agent":"Mozilla/5.0"
}


#########################################
# LOAD DATABASE
#########################################

try:
    with open(PRICE_FILE,"r") as f:
        prices=json.load(f)
except:
    prices={}



#########################################
# PUSH ALERT
#########################################

def push(title,body,url):

    try:

        requests.post(
            "https://api.pushbullet.com/v2/pushes",
            headers={"Access-Token":PUSH_TOKEN},
            json={
                "type":"link",
                "title":title,
                "body":body,
                "url":url
            },
            timeout=20
        )

        print("Push Sent")

    except Exception as e:

        print("Push Error:",e)



#########################################
# GET PRICE SHOPIFY ENGINE
#########################################

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

    except:

        return None,None



#########################################
# SCAN WEBSITE
#########################################

def scan():

    products={}

    print("Scanning Outfitters AI v4...")

    for page in range(1,MAX_PAGES+1):

        try:

            url=BASE+str(page)

            r=requests.get(url,headers=HEADERS,timeout=20)

            soup=BeautifulSoup(r.text,"html.parser")

            links=soup.find_all("a",href=True)

            for link in links:

                href=link["href"]

                if "/products/" in href:

                    full="https://outfitters.com.pk"+href.split("?")[0]

                    name=link.text.strip()

                    if len(name)>4:

                        products[full]=name


            print("Page",page,"OK")

        except:

            print("Page",page,"error")


    return products



#########################################
# MAIN LOOP
#########################################

while True:

    print("\nChecking products...\n")

    products=scan()

    print("Total Products:",len(products))


    for url,name in products.items():

        price,compare=get_price(url)

        if price is None:
            continue

        print(name,"=",price)

        old=prices.get(url)


        ##################################
        # NEW PRODUCT ALERT
        ##################################

        if old is None:

            prices[url]=price

            message=f"""

NEW PRODUCT

{name}

Price: PKR {price}

{url}

"""

            push(
            "🆕 New Product Detected",
            message,
            url
            )

            continue



        ##################################
        # PRICE CHANGE ALERT
        ##################################

        if price!=old:

            diff=price-old

            if diff<0:
                status="⬇ PRICE DROP"
            else:
                status="⬆ PRICE INCREASE"


            message=f"""

{name}

{status}

Old: PKR {old}
New: PKR {price}

{url}

"""

            push(
            "🔥 Price Changed",
            message,
            url
            )

            prices[url]=price



        ##################################
        # FLASH SALE ALERT
        ##################################

        if compare:

            discount=int((compare-price)/compare*100)

            if discount>=70:

                message=f"""

{name}

🔥 FLASH SALE {discount}%

Old: PKR {compare}
Now: PKR {price}

{url}

"""

                push(
                "🔥 FLASH SALE DETECTED",
                message,
                url
                )


    with open(PRICE_FILE,"w") as f:

        json.dump(prices,f)


    print("\nSleeping",CHECK_INTERVAL,"seconds\n")

    time.sleep(CHECK_INTERVAL)