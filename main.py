import requests
import smtplib
import time
from email.mime.text import MIMEText

print("===== OUTFITTERS TRACKER STARTED =====", flush=True)

# Product API (Stable Method)
PRODUCT_API = "https://outfitters.com.pk/products/quilted-puffer-jacket-with-hood-1.js"

# Email Settings
sender = "raufamin7871@gmail.com"
password = "sjah fxag vdos gejj"
receiver = "raufamin7871@gmail.com"


def get_price():

    print("Fetching price...", flush=True)

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

    return price,discount


def send_email(price, discount):

    subject = "🔥 Outfitters Price Alert"

    body = f"""
Price Update Detected

Price: Rs {price}

Discount: {discount}% OFF

https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1
"""

    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    try:

        print("Connecting SMTP...", flush=True)

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)

        server.starttls()

        print("Logging in...", flush=True)

        server.login(sender, password)

        print("Sending Email...", flush=True)

        server.sendmail(sender, receiver, msg.as_string())

        server.quit()

        print("Email Sent Successfully", flush=True)

    except Exception as e:

        print("EMAIL ERROR:", e, flush=True)


old_price=None


while True:

    try:

        price,discount=get_price()

        print("Current Price:",price,flush=True)

        if old_price is None:

            send_email(price,discount)

            old_price=price

        elif price!=old_price:

            send_email(price,discount)

            old_price=price

        time.sleep(300)

    except Exception as e:

        print("ERROR:",e,flush=True)

        time.sleep(60)