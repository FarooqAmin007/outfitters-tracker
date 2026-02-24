import requests
import time

print("===== GOD TRACKER AI ELITE STARTED =====")


# ========= PUSH TOKEN =========

PUSH_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"


# ========= WEBSITE =========

SITE_URL = "https://outfitters.com.pk/collections/all/products.json"


# ========= MEMORY =========

last_prices = {}
lowest_prices = {}
stock_state = {}
known_products = set()

FIRST_RUN = True


# ========= PUSH =========

def send_push(title,message):

    try:

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
            },
            timeout=10
        )

        print("Push:",title)

    except Exception as e:

        print("Push error:",e)



# ========= GET PRODUCTS =========

def get_products():

    try:

        r = requests.get(SITE_URL,timeout=30)

        return r.json()["products"]

    except Exception as e:

        print("Website error:",e)

        return []



# ========= DEAL AI =========

def deal_score(price,discount):

    score = discount*2

    if price < 5000:
        score += 30

    if discount >= 70:
        score += 80

    return score



# ========= MAIN LOOP =========

while True:

    try:

        print("\nScanning Outfitters AI ELITE...")

        products = get_products()

        print("Products:",len(products))


        best_score = 0
        best_product = None


        for product in products:

            name = product["title"]

            variant = product["variants"][0]

            price = int(float(variant["price"]))

            compare = variant["compare_at_price"]

            stock = variant["available"]


            if compare:

                compare=int(float(compare))
                discount=int((1-price/compare)*100)

            else:

                discount=0


            # ========= FIRST RUN SAVE =========

            if FIRST_RUN:

                last_prices[name]=price
                lowest_prices[name]=price
                stock_state[name]=stock
                known_products.add(name)
                continue


            # ========= NEW PRODUCT =========

            if name not in known_products:

                known_products.add(name)

                send_push(

                "🆕 New Product",

                f"{name}\nPKR {price}"

                )


            # ========= PRICE CHANGE =========

            old_price=last_prices.get(name)

            if old_price and price!=old_price:

                direction="📉 Drop" if price<old_price else "📈 Increase"

                send_push(

                "🔥 Price Change",

                f"{name}\n\n"
                f"{old_price} → {price}\n"
                f"{direction}\n"
                f"Discount {discount}%"

                )

                last_prices[name]=price


            # ========= LOWEST PRICE =========

            if price<lowest_prices.get(name,price):

                lowest_prices[name]=price

                send_push(

                "🏆 Lowest Price",

                f"{name}\nPKR {price}"

                )


            # ========= STOCK ALERT =========

            old_stock=stock_state.get(name)

            if old_stock!=stock:

                if stock:

                    send_push(

                    "✅ Restock",

                    f"{name}\nAvailable Now"

                    )

                else:

                    send_push(

                    "❌ Out Of Stock",

                    f"{name}"

                    )

                stock_state[name]=stock


            # ========= MEGA SALE =========

            if discount>=70:

                send_push(

                "💰 MEGA SALE",

                f"{name}\n"
                f"PKR {price}\n"
                f"{discount}% OFF"

                )


            # ========= AI BEST DEAL =========

            score=deal_score(price,discount)

            if score>best_score:

                best_score=score
                best_product=(name,price,discount)


        if not FIRST_RUN and best_product:

            name,price,discount=best_product

            send_push(

            "🤖 AI BEST DEAL",

            f"{name}\nPKR {price}\n{discount}% OFF"

            )


        FIRST_RUN=False


        print("Sleeping 10 minutes...")

        time.sleep(600)


    except Exception as e:

        print("CRASH PROTECTED:",e)

        time.sleep(60)