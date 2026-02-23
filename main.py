import requests
import smtplib
import time
import os

print("===== TRACKER BOOTING =====")

# Product API
PRODUCT_API = "https://outfitters.com.pk/products/quilted-puffer-jacket-with-hood-1.js"

# Email Settings (Variables first, fallback to hardcoded)
EMAIL_SENDER = os.getenv("EMAIL_SENDER") or "raufamin7871@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or "tzvv dnlf tkuy bksl"

EMAIL_RECEIVER = "raufamin7871@gmail.com"

last_price = None


def get_product():

    print("Fetching product...")

    r = requests.get(PRODUCT_API, timeout=10)

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


def send_email(subject,body):

    print("Sending email...")

    server=smtplib.SMTP_SSL("smtp.gmail.com",465)

    server.login(
        EMAIL_SENDER,
        EMAIL_PASSWORD
    )

    message=f"Subject:{subject}\n\n{body}"

    server.sendmail(
        EMAIL_SENDER,
        EMAIL_RECEIVER,
        message
    )

    server.quit()

    print("Email Sent OK")


print("Tracker Starting...")


while True:

    try:

        price,compare,discount=get_product()

        print("Current Price:",price)
        print("Discount:",discount)

        if last_price is None:

            send_email(
                "Tracker Started",
                f"""

Tracker is LIVE

Price: Rs {price}
Original: Rs {compare}
Discount: {discount}% OFF

You will get alerts when price changes.

"""
            )

            last_price=price

        elif price!=last_price:

            send_email(
                "Price Changed",
                f"""

New Price: Rs {price}

Original: Rs {compare}

Discount: {discount}% OFF

"""
            )

            last_price=price


        time.sleep(300)


    except Exception as e:

        print("ERROR:",e)

        time.sleep(60)