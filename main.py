import requests
import json
import time

PUSHBULLET_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

URL = "https://outfitters.com.pk/products.json?limit=250"

STATE_FILE = "state.json"


print("===== GOD MODE AI HUNTER QUANTUM v7 STARTED =====")


# Load memory
try:
    with open(STATE_FILE,"r") as f:
        state=json.load(f)
except:
    state={}


def push(title,msg):

    requests.post(
        "https://api.pushbullet.com/v2/pushes",
        headers={
            "Access-Token":PUSHBULLET_TOKEN
        },
        json={
            "type":"note",
            "title":title,
            "body":msg
        }
    )


def price_clean(price):

    try:
        return int(float(price))
    except:
        return 0


print("Scanning Outfitters realtime...")


r=requests.get(URL)
data=r.json()

products=data["products"]

print("Products found:",len(products))


new_state={}

alerts=0


for p in products:

    title=p["title"]

    variant=p["variants"][0]

    price=price_clean(variant["price"])

    compare=price_clean(variant["compare_at_price"])

    key=str(p["id"])


    new_state[key]={

        "title":title,
        "price":price,
        "compare":compare

    }


    if key in state:

        old_price=state[key]["price"]

        if price!=old_price:

            alerts+=1

            msg=f"""
{title}

Old Price: Rs {old_price}
New Price: Rs {price}

https://outfitters.com.pk/products/{p['handle']}
"""

            print("PRICE CHANGE:",title)

            push("PRICE CHANGE",msg)


    else:

        alerts+=1

        msg=f"""
NEW PRODUCT

{title}

Price Rs {price}

https://outfitters.com.pk/products/{p['handle']}
"""

        print("NEW:",title)

        push("NEW PRODUCT",msg)


# Save memory
with open(STATE_FILE,"w") as f:
    json.dump(new_state,f)


print("Alerts sent:",alerts)

print("Scan complete.")

