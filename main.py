import smtplib
from email.mime.text import MIMEText

def send_email(price, discount):

    sender = "raufamin7871@gmail.com"
    password = "sjah fxag vdos gejj"
    receiver = "raufamin7871@gmail.com"

    subject = "🔥 Price Alert!"
    body = f"Price: {price}\nDiscount: {discount}%"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    try:
        print("Connecting SMTP...")

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
        server.starttls()

        print("Logging in...")

        server.login(sender, password)

        print("Sending...")

        server.sendmail(sender, receiver, msg.as_string())

        server.quit()

        print("Email Sent Successfully")

    except Exception as e:
        print("EMAIL ERROR:", e)