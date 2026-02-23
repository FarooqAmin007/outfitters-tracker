import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# =============================
# PRODUCT URL
# =============================

URL = "https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1?variant=44728895373503"


# =============================
# EMAIL SETTINGS
# =============================

SENDER_EMAIL = "raufamin7871@gamil.com"
APP_PASSWORD = "sjah fxag vdos gejj"
RECEIVER_EMAIL = "raufamin7871@gmail.com"


# =============================
# GET PRICE
# =============================

def get_price():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    price = soup.find("span", {"class": "price-item--regular"})

    if price:
        price_text = price.get_text().strip()
        price_number = float(
    price_text.replace("Rs.", "")
    .replace("PKR", "")
    .replace(",", "")
    .strip()
)
        return price_number

    return None


# =============================
# SEND EMAIL (PORT 465 SSL)
# =============================

def send_email(price):

    subject = "🔥 Outfitters Price Alert"
    body = f"Current Price: {price}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:

        print("Connecting SMTP SSL 465...")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)

        print("Logging in...")

        server.login(SENDER_EMAIL, APP_PASSWORD)

        print("Sending Email...")

        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        server.quit()

        print("✅ Email Sent Successfully")

    except Exception as e:

        print("❌ EMAIL ERROR:", e)


# =============================
# MAIN
# =============================

print("===== OUTFITTERS TRACKER STARTED =====")

print("Fetching price...")

price = get_price()

print("Current Price:", price)

if price:
    send_email(price)
else:
    print("Price not found")