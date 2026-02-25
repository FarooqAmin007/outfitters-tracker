import requests
import time
import json
import random

print("===== GOD MODE AI HUNTER QUANTUM v2.1 STARTED =====")

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

        print("Push:",title)

    except Exception as e:

        print("Push Error:",e)



# STATE
def load_state():

    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}


def save_state(s):

    with open(STATE_FILE,"w") as f:
        json.dump(s,f)



# DISCOUNT
def discount(old,new):

    if old==0:
        return 0

    return int((old-new)/old*100)



# MASTER PRODUCT SCAN
def scan_products():

    print("Scanning Shopify master API...")

    url=f"{BASE_URL}/products.json?limit=250"

    r=requests.get(url,headers=HEADERS,timeout=30)

    data=r.json()

    return data["products"]



# QUANTUM ENGINE
def quantum():

    state=load_state()

    new_state={}

    total=0

    products=scan_products()

    print("Products found:",len(products))


    for p in products:

        name=p["title"]

        handle=p["handle"]

        link=f"{BASE_URL}/products/{handle}"


        for v in p["variants"]:

            variant=v["title"]

            key=handle+"-"+variant

            # FIXED PRICE PARSER
            price=int(float(v["price"]))

            available=v["available"]

            total+=1

            new_state[key]=price

            old=state.get(key)

            print(name,"=",price)


            # FIRST SAVE
            if old is None:

                push(
                "🆕 NEW PRODUCT",
                f"{name}\n{price}\n{link}"
                )


            else:

                if price!=old:

                    d=discount(old,price)

                    push(
                    "💰 PRICE CHANGE",
                    f"{name}\n{old} → {price}\n{d}%\n{link}"
                    )


                    if d>=30:

                        push(
                        "🔥 SALE ALERT",
                        f"{name}\n{d}% OFF\n{price}\n{link}"
                        )


                    if d>=70:

                        push(
                        "⚠️ MEGA SALE",
                        f"{name}\n{old} → {price}\n{link}"
                        )


            # RESTOCK
            if available and key not in state:

                push(
                "📦 RESTOCK",
                f"{name}\nBack in stock\n{link}"
                )


    save_state(new_state)

    print("Products scanned:",total)



# LOOP
while True:

    try:

        print("Checking products...")

        quantum()

        sleep=random.randint(
        CHECK_INTERVAL-30,
        CHECK_INTERVAL+30
        )

        print("Sleeping:",sleep)

        time.sleep(sleep)


    except Exception as e:

        print("CRITICAL ERROR:",e)

        time.sleep(60)