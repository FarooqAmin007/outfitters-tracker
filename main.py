import requests
import time
import json
import random

print("===== GOD MODE QUANTUM v3 STEALTH STARTED =====")

BASE_URL = "https://outfitters.com.pk"

STATE_FILE = "quantum_state.json"

CHECK_INTERVAL = 180

PUSH_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

HEADERS = {
"User-Agent":"Mozilla/5.0"
}


# PUSHBULLET
def push(title,message):

    try:

        requests.post(
        "https://api.pushbullet.com/v2/pushes",
        json={
        "type":"note",
        "title":title,
        "body":message
        },
        headers={
        "Access-Token":PUSH_TOKEN
        }
        )

        print("Push Sent:",title)

    except Exception as e:

        print("Push Error:",e)



# LOAD STATE
def load_state():

    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}



# SAVE STATE
def save_state(s):

    with open(STATE_FILE,"w") as f:
        json.dump(s,f)



# DISCOUNT
def discount(old,new):

    if old==0:
        return 0

    return int((old-new)/old*100)



# SCAN PRODUCTS
def scan_products():

    url=f"{BASE_URL}/products.json?limit=250"

    r=requests.get(url,headers=HEADERS,timeout=30)

    return r.json()["products"]



# QUANTUM ENGINE
def quantum():

    state=load_state()

    new_state={}

    products=scan_products()

    total_products=0
    price_changes=0
    sales_found=0


    for p in products:

        name=p["title"]

        handle=p["handle"]

        link=f"{BASE_URL}/products/{handle}"


        for v in p["variants"]:

            key=handle+"-"+v["title"]

            price=int(float(v["price"]))

            new_state[key]=price

            old=state.get(key)

            total_products+=1


            if old is None:
                continue


            if price!=old:

                price_changes+=1

                d=discount(old,price)

                push(
                "💰 Price Change",
                f"{name}\n{old} → {price}\n{link}"
                )


                if d>=30:

                    sales_found+=1

                    push(
                    "🔥 Sale Alert",
                    f"{name}\n{d}% OFF\n{price}\n{link}"
                    )


                if d>=70:

                    push(
                    "⚠️ MEGA SALE",
                    f"{name}\n{old} → {price}\n{link}"
                    )


    save_state(new_state)


    print("Products scanned:",total_products)
    print("Price changes:",price_changes)
    print("Sales found:",sales_found)



# LOOP
while True:

    try:

        quantum()

        sleep=random.randint(150,210)

        print("Sleeping:",sleep)

        time.sleep(sleep)


    except Exception as e:

        print("Error:",e)

        time.sleep(60)