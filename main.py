import requests
from bs4 import BeautifulSoup
import smtplib
import socket
import time
from email.mime.text import MIMEText

print("===== OUTFITTERS TRACKER STARTED =====")

# PRODUCT URL
URL = "https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1?variant=44728895373503"

# EMAIL SETTINGS
EMAIL = "raufamin7871@gmail.com"
PASSWORD = "sjah fxag vdos gejj"


# -------------------------
# NETWORK TEST
# -------------------------

print("Testing SMTP connection...")

try:
    socket.create_connection(("smtp.gmail.com", 465), 10)
    print("✅ SMTP 465 reachable")
except Exception as e:
    print("❌ SMTP BLOCKED:", e)


# -------------------------
# GET PRICE
# -------------------------

def get_price():

    print("Fetching price...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    price_text = soup.find("span", {"class":"price-item--sale"}).text.strip()

    # Clean PKR price
    price_number = float(
        price_text
        .replace("PKR","")
        .replace("Rs.","")
        .replace(",","")
        .strip()
    )

    print("Current Price:", price_number)

    return price_number


# -------------------------
# SEND EMAIL
# -------------------------

def send_email(price):

    print("Connecting SMTP SSL 465...")

    subject = "🔥 Outfitters Price Alert"

    body = f"""
Product Price Changed!

Price = {price}

Link:
{URL}
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    try:

        server = smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=30)

        server.login(EMAIL,PASSWORD)

        server.sendmail(
            EMAIL,
            EMAIL,
            msg.as_string()
        )

        server.quit()

        print("✅ EMAIL SENT SUCCESSFULLY")

    except Exception as e:

        print("❌ EMAIL ERROR:",e)


# -------------------------
# RUN
# -------------------------

price = get_price()

send_email(price)

print("Tracker Completed")