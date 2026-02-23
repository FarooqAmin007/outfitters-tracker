import requests
import smtplib
import time

#━━━━━━━━━━━━━━━━━━━━━━━
# PRODUCT API
#━━━━━━━━━━━━━━━━━━━━━━━

PRODUCT_API = "https://outfitters.com.pk/products/quilted-puffer-jacket-with-hood-1.js"

#━━━━━━━━━━━━━━━━━━━━━━━
# EMAIL SETTINGS
#━━━━━━━━━━━━━━━━━━━━━━━

EMAIL_SENDER = "raufamin7871@gmail.com"
EMAIL_PASSWORD = "tzvv dnlf tkuy bksl "

EMAIL_RECEIVER = "raufamin7871@gmail.com"

TARGET_DISCOUNT = 70

#━━━━━━━━━━━━━━━━━━━━━━━
# STORAGE
#━━━━━━━━━━━━━━━━━━━━━━━

last_price = 0
last_discount = 0


def get_product():

    r = requests.get(PRODUCT_API)

    data = r.json()

    prices = []
    compares = []

    for v in data["variants"]:

        price = float(v["price"]) / 100
        compare = float(v["compare_at_price"] or 0) / 100

        prices.append(price)
        compares.append(compare)

    min_price = min(prices)
    max_compare = max(compares)

    discount = int((1 - min_price/max_compare)*100)

    return min_price, max_compare, discount


def send_email(price, compare, discount):

    subject = "🔥 CLOUD PRICE ALERT"

    body = f"""
Price Drop Detected!

Price = Rs {price}

Original = Rs {compare}

Discount = {discount}% OFF

https://outfitters.com.pk/products/quilted-puffer-jacket-with-hood-1
"""

    message = f"Subject: {subject}\n\n{body}"

    server = smtplib.SMTP_SSL("smtp.gmail.com",465)

    server.login(
        EMAIL_SENDER,
        EMAIL_PASSWORD
    )

    server.sendmail(
        EMAIL_SENDER,
        EMAIL_RECEIVER,
        message
    )

    server.quit()


while True:

    price, compare, discount = get_product()

    print(price, discount)

    if discount >= TARGET_DISCOUNT:

        send_email(price, compare, discount)

        TARGET_DISCOUNT = 999

    time.sleep(300)
