import requests
import time
import json
import random

print("===== GOD MODE AI HUNTER QUANTUM STARTED =====")

# ========= SETTINGS =========

BASE_URL = "https://outfitters.com.pk"

COLLECTIONS = [
"/collections/men",
"/collections/women",
"/collections/kids",
"/collections/sale",
"/collections/new-arrivals"
]

CHECK_INTERVAL = 120

STATE_FILE = "quantum_state.json"

PUSH_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

HEADERS = {
"User-Agent":"Mozilla/5.0 (Quantum Tracker)"
}

DISCOUNT_LEVELS = [30,40,50,60,70,80,90]


# ========= PUSH =========

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


# ========= STATE =========

def load_state():

    try:
        with open(STATE_FILE) as f:
            return json.load(f)

    except:
        return {}


def save_state(s):

    with open(STATE_FILE,"w") as f:
        json.dump(s,f)


# ========= DISCOUNT =========

def discount(old,new):

    if old==0:
        return 0

    return int((old-new)/old*100)


# ========= SCAN COLLECTION FAST =========

def scan_collection(collection):

    products_all=[]

    page=1

    while True:

        url=f"{BASE_URL}{collection}/products.json?limit=250&page={page}"

        r=requests.get(url,headers=HEADERS,timeout=20)

        data=r.json()

        products=data["products"]

        if not products:
            break

        products_all.extend(products)

        page+=1

    return products_all


# ========= QUANTUM SCAN =========

def quantum_scan():

    print("Quantum scanning...")

    state=load_state()

    new_state={}

    total=0

    for collection in COLLECTIONS:

        try:

            products=scan_collection(collection)

            for p in products:

                name=p["title"]

                handle=p["handle"]

                link=f"{BASE_URL}/products/{handle}"

                for v in p["variants"]:

                    variant=v["title"]

                    key=handle+"-"+variant

                    price=int(v["price"])

                    available=v["available"]

                    total+=1

                    new_state[key]=price

                    old_price=state.get(key)

                    print(name,variant,"=",price)

                    # NEW PRODUCT

                    if old_price is None:

                        push(
                        "🆕 NEW PRODUCT",
                        f"{name}\n{variant}\nPrice {price}\n{link}"
                        )


                    else:

                        if price!=old_price:

                            d=discount(old_price,price)

                            push(
                            "💰 PRICE CHANGE",
                            f"{name}\n{variant}\n{old_price} → {price}\n{d}%\n{link}"
                            )

                            # BIG DISCOUNT

                            for level in DISCOUNT_LEVELS:

                                if d>=level:

                                    push(
                                    f"🔥 {level}% SALE",
                                    f"{name}\nNow {price}\n{link}"
                                    )


                            # EXTREME DROP

                            if d>=70:

                                push(
                                "⚠️ EXTREME DROP",
                                f"{name}\n{old_price} → {price}\n{link}"
                                )


                            # SMALL DROP

                            if old_price>price and d<20:

                                push(
                                "📉 SMALL DROP",
                                f"{name}\n{old_price} → {price}\n{link}"
                                )


                    # RESTOCK

                    if available and key not in state:

                        push(
                        "📦 RESTOCK",
                        f"{name}\n{variant}\nBack in stock\n{link}"
                        )


        except Exception as e:

            print("Collection Error:",e)


    save_state(new_state)

    print("Products scanned:",total)


# ========= QUANTUM ENGINE =========

while True:

    try:

        quantum_scan()

        sleep=random.randint(
        CHECK_INTERVAL-20,
        CHECK_INTERVAL+20
        )

        print("Sleeping:",sleep)

        time.sleep(sleep)

    except Exception as e:

        print("CRITICAL ERROR:",e)

        time.sleep(60)