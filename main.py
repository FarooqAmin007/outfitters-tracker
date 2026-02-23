import requests
import smtplib
import time
import os

#━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRODUCT API
#━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRODUCT_API = "https://outfitters.com.pk/products/quilted-puffer-jacket-with-hood-1.js"

EMAIL_SENDER = os.getenv("raufamin7871@gmail.com")
EMAIL_PASSWORD = os.getenv("tzvv dnlf tkuy bksl ")

EMAIL_RECEIVER = "raufamin7871@gmail.com"

#━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STORAGE
#━━━━━━━━━━━━━━━━━━━━━━━━━━━

last_price = None
started = False


#━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET PRODUCT DATA
#━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_product():

    r = requests.get(PRODUCT_API)

    data = r.json()

    prices=[]
    compares=[]

    for v in data["variants"]:

        prices.append(float(v["price"])/100)
        compares.append(float(v["compare_at_price"] or 0)/100)

    price=min(prices)
    compare=max(compares)

    discount=int((1-price/compare)*100)

    return price,compare,discount


#━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EMAIL
#━━━━━━━━━━━━━━━━━━━━━━━━━━━

def send_email(subject,body):

    message=f"Subject:{subject}\n\n{body}"

    server=smtplib.SMTP_SSL("smtp.gmail.com",465)

    server.login(EMAIL_SENDER,EMAIL_PASSWORD)

    server.sendmail(
        EMAIL_SENDER,
        EMAIL_RECEIVER,
        message
    )

    server.quit()


#━━━━━━━━━━━━━━━━━━━━━━━━━━━
# START MESSAGE
#━━━━━━━━━━━━━━━━━━━━━━━━━━━

price,compare,discount=get_product()

send_email(
"✅ Tracker Started",
f"""

Outfitters Tracker is LIVE

Current Price: Rs {price}

Original Price: Rs {compare}

Discount: {discount}% OFF

You will receive alerts when price changes.

https://outfitters.com.pk/products/quilted-puffer-jacket-with-hood-1

"""
)

last_price=price

print("Tracker Started Successfully")
print("Price:",price,"Discount:",discount)


#━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN LOOP
#━━━━━━━━━━━━━━━━━━━━━━━━━━━

while True:

    price,compare,discount=get_product()

    print("Checking...",price)

    if price!=last_price:

        send_email(
"🔥 Price Changed",
f"""

PRICE CHANGE DETECTED

New Price: Rs {price}

Original Price: Rs {compare}

Discount: {discount}% OFF

https://outfitters.com.pk/products/quilted-puffer-jacket-with-hood-1

"""
)

        last_price=price

    time.sleep(300)