import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os

print("===== ULTRA TRACKER V2 STARTED =====")
print(f"Running on Railway at {time.strftime('%Y-%m-%d %H:%M:%S')}")

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

# ===== GET PRICE FUNCTION WITH BROWSERLESS =====
def get_price(url):
    # Get Browserless URL from Railway environment variables
    # Railway will automatically set this when you add the Browserless service
    browserless_url = os.environ.get("BROWSERLESS_URL", "http://browserless:3000")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        print(f"🔌 Connecting to Browserless at: {browserless_url}")
        driver = webdriver.Remote(
            command_executor=f'{browserless_url}/webdriver',
            options=chrome_options
        )
        
        print("🌐 Loading page...")
        driver.get(url)
        
        # Wait for page to load (adjust time if needed)
        time.sleep(5)
        
        # Try multiple methods to find the price
        price = None
        
        # Method 1: Look for common price selectors
        selectors = [
            "span.price",
            "div.price",
            "span.actual-price",
            "span.product-price",
            "span[class*='price']",
            "div[class*='price']",
            "span.money",
            ".product__price",
            ".product-price",
            ".price-item"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    price_text = element.text.strip()
                    if price_text and re.search(r'[\d,]+', price_text):
                        match = re.search(r'[\d,]+', price_text)
                        if match:
                            price = int(match.group().replace(",", ""))
                            print(f"💰 Found price with selector '{selector}': {price}")
                            driver.quit()
                            return price
            except:
                continue
        
        # Method 2: Get all text and search for price patterns
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        patterns = [
            r'PKR\s*([0-9,]+)',
            r'Rs\.?\s*([0-9,]+)',
            r'Price[:\s]*([0-9,]+)',
            r'([0-9,]+)\s*PKR',
            r'\b([0-9,]+)\s*Rs\.?\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_text)
            if match:
                price = int(match.group(1).replace(",", ""))
                print(f"💰 Found price with regex: {price}")
                driver.quit()
                return price
        
        # Method 3: Check meta tags
        meta_selectors = [
            "meta[property='product:price:amount']",
            "meta[name='price']",
            "meta[itemprop='price']"
        ]
        
        for selector in meta_selectors:
            try:
                meta = driver.find_element(By.CSS_SELECTOR, selector)
                content = meta.get_attribute("content")
                if content:
                    price = int(float(content))
                    print(f"💰 Found price in meta: {price}")
                    driver.quit()
                    return price
            except:
                continue
        
        print("❌ Price not found on page")
        driver.quit()
        return None
        
    except Exception as e:
        print(f"❌ Error with Browserless: {e}")
        return None

# ===== MAIN LOOP =====
print("Starting price tracking with Browserless...")
print(f"Tracking {len(products)} product(s)\n")

# Track consecutive failures to avoid excessive logging
failures = 0

while True:
    try:
        print("=" * 50)
        print(f"Checking products at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        for name, url in products.items():
            print(f"\n📦 Checking: {name}")
            print(f"🔗 URL: {url}")
            
            price = get_price(url)

            if price is None or price == 0:
                print(f"❌ {name}: Price not found")
                failures += 1
                if failures > 3:
                    print("⚠️ Multiple failures, but continuing...")
                continue
            
            # Reset failure counter on success
            failures = 0

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
                    f"🔗 {url}"
                )

                last_prices[name] = price

            else:
                print(f"⏸️ No change (still PKR {price:,})")

        print(f"\n⏱️ Waiting 5 minutes until next check...\n")
        time.sleep(300)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        break
    except Exception as e:
        print(f"❌ Unexpected error in main loop: {e}")
        print("⏱️ Waiting 30 seconds before retry...")
        time.sleep(30)