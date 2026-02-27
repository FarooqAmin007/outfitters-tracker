import requests
import json

print("===== GOD MODE AI HUNTER QUANTUM v8.2 TURBO STARTED =====")

STATE_FILE = "state.json"
NTFY_TOPIC = "outfitters-amin"


# LOAD MEMORY
try:
    with open(STATE_FILE,"r") as f:
        old_prices=json.load(f)
except:
    old_prices={}


# PUSH NOTIFICATION
def send_push(title,message):

    try:

        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={"Title":title}
        )

        print("Push sent")

    except Exception as e:

        print("Push Error:",e)



# GET PRODUCTS (DEDUPLICATED)
def get_products():

    products={}

    page=1

    while True:

        url=f"https://outfitters.com.pk/products.json?limit=250&page={page}"

        r=requests.get(url,timeout=20)

        data=r.json()

        if not data["products"]:
            break


        for p in data["products"]:

            title=p["title"]
            handle=p["handle"]

            url=f"https://outfitters.com.pk/products/{handle}"

            # get lowest variant price
            prices=[float(v["price"]) for v in p["variants"]]

            price=min(prices)

            key=handle  # unique id

            products[key]={

                "title":title,
                "price":price,
                "url":url
            }


        page+=1


    return products



print("Scanning Outfitters fast mode...")

products=get_products()

print("Real products found:",len(products))


new_prices={}

alerts=0


for key,p in products.items():

    title=p["title"]
    price=p["price"]
    url=p["url"]

    new_prices[key]=price


    # NEW PRODUCT
    if key not in old_prices:

        send_push(
            "New Product",
            f"""{title}

Price: PKR {price}

{url}
"""
        )

        print("NEW:",title)

        alerts+=1


    # PRICE CHANGE
    else:

        old_price=old_prices[key]

        if price!=old_price:

            percent=((price-old_price)/old_price)*100

            send_push(
                "Price Changed",
                f"""{title}

Old: PKR {old_price}
New: PKR {price}

Change: {round(percent,2)}%

{url}
"""
            )

            print("PRICE CHANGE:",title)

            alerts+=1



# SAVE MEMORY
with open(STATE_FILE,"w") as f:

    json.dump(new_prices,f)



print("Alerts:",alerts)

print("Scan complete.")
