import requests
from bs4 import BeautifulSoup
import time
import re
import json

print("===== ULTRA TRACKER V2 STARTED =====")

# ===== PUSHBULLET TOKEN =====
PUSH_TOKEN = "o.LMvhCtQSfJMHLEXu1ghkK7NOxYpwHlyc"

# ===== PRODUCTS =====
products = {
    "Puffer Jacket": "https://outfitters.com.pk/collections/men-outerwear/products/quilted-puffer-jacket-with-hood-1?variant=44728895373503"
}

# ===== STORE LAST PRICES =====
last_prices = {}

# ===== PUSH FUNCTION =====
def send_push(title, message):
    try:
        requests.post(
            "https://api.pushbullet.com/v2/pushes",
            headers={
                "Access-Token": PUSH_TOKEN,
                "Content-Type": "application/json"
            },
            json={
                "type": "note",
                "title": title,
                "body": message
            }
        )
        print("✅ Push Sent")
    except Exception as e:
        print(f"❌ Push failed: {e}")

# ===== GET PRICE FUNCTION =====
def get_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Method 1: Look for price in meta tags (often contains product data)
        meta_price = soup.find("meta", property="product:price:amount")
        if meta_price and meta_price.get("content"):
            price = int(float(meta_price.get("content")))
            print(f"Found price in meta: {price}")
            return price
        
        # Method 2: Look for JSON-LD structured data
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check for offers in the JSON data
                    if "offers" in data:
                        offers = data["offers"]
                        if isinstance(offers, dict) and "price" in offers:
                            price = int(float(offers["price"]))
                            print(f"Found price in JSON-LD: {price}")
                            return price
                    elif "price" in data:
                        price = int(float(data["price"]))
                        print(f"Found price in JSON-LD: {price}")
                        return price
            except:
                continue
        
        # Method 3: Look for product price in specific classes
        price_selectors = [
            "span.price",
            "div.price",
            "span.actual-price",
            "span.product-price",
            "span[class*='price']",
            "div[class*='price']",
            "span.money",
            "span.woocommerce-Price-amount"
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text().strip()
                # Extract numbers from price text
                match = re.search(r'[\d,]+', price_text)
                if match:
                    price = int(match.group().replace(",", ""))
                    print(f"Found price in HTML element: {price}")
                    return price
        
        # Method 4: Regex search in entire page text (your original method)
        text = soup.get_text()
        # Try different price patterns
        patterns = [
            r'PKR\s*([0-9,]+)',
            r'Rs\.?\s*([0-9,]+)',
            r'Price[:\s]*([0-9,]+)',
            r'([0-9,]+)\s*PKR',
            r'\b([0-9,]+)\s*Rs\.?\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price = int(match.group(1).replace(",", ""))
                print(f"Found price with regex: {price}")
                return price
        
        # Method 5: Look for variant price in the HTML
        variant_id = url.split("variant=")[-1] if "variant=" in url else None
        if variant_id:
            # Sometimes price is in a script with variant data
            variant_pattern = rf'id"{variant_id}".*?price":(\d+)'
            variant_match = re.search(variant_pattern, r.text.replace(" ", ""))
            if variant_match:
                price = int(variant_match.group(1))
                print(f"Found variant price: {price}")
                return price
        
        print(f"❌ Price not found for {url}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        return None

# ===== MAIN LOOP =====
print("Starting price tracking...")
print(f"Tracking {len(products)} product(s)\n")

while True:
    print("=" * 50)
    print(f"Checking products at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    for name, url in products.items():
        print(f"\n📦 Checking: {name}")
        print(f"🔗 URL: {url}")
        
        price = get_price(url)

        if price is None:
            print(f"❌ {name}: Price not found")
            continue

        print(f"💰 {name} = PKR {price:,}")

        old_price = last_prices.get(name)

        # First time only save
        if old_price is None:
            last_prices[name] = price
            print(f"💾 First price saved: PKR {price:,}")
            continue

        # PRICE CHANGE ALERT
        if price != old_price:
            if price < old_price:
                change_type = "📉 Price Dropped"
                emoji = "⬇️"
            else:
                change_type = "📈 Price Increased"
                emoji = "⬆️"

            print(f"{emoji} Price changed from PKR {old_price:,} to PKR {price:,}")

            send_push(
                "🔥 Outfitters Price Change Alert!",
                f"{name}\n\n"
                f"{change_type}\n"
                f"{'─' * 30}\n"
                f"Old Price: PKR {old_price:,}\n"
                f"New Price: PKR {price:,}\n"
                f"Difference: PKR {abs(price - old_price):,}\n"
                f"{'─' * 30}\n"
                f"{change_type}\n\n"
                f"🔗 {url}"
            )

            last_prices[name] = price

        else:
            print(f"⏸️ No change (still PKR {price:,})")

    print(f"\n⏱️ Waiting 5 minutes until next check...\n")
    time.sleep(300)