import os
import requests
import time
import logging
from telegram import Bot

# Load secrets from GitHub Actions
TELBOT_TOKEN = os.getenv("TELBOT_TOKEN")  # Telegram Bot Token
CJ_API_KEY = os.getenv("CJ_API_KEY")  # CJ Dropshipping API Key
CHANNEL_ID = "-1002268570632"  # Replace with your actual Telegram Channel ID

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# CJ API Endpoints
CJ_PRODUCT_LIST_URL = "https://developers.cjdropshipping.com/api2.0/v1/product/list"
CJ_FREIGHT_CALCULATE_URL = "https://developers.cjdropshipping.com/api2.0/v1/logistic/freightCalculate"

# Initialize Telegram Bot
bot = Bot(token=TELBOT_TOKEN)

def fetch_products():
    """
    Fetch products from CJ Dropshipping API.
    """
    headers = {"CJ-Access-Token": CJ_API_KEY, "Content-Type": "application/json"}
    params = {"pageSize": 5, "pageNum": 1}  # Fetch 5 products per request
    response = requests.get(CJ_PRODUCT_LIST_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["code"] == 200:
            return data["data"]["list"]
        else:
            logging.error(f"Error from CJ API: {data['message']}")
    else:
        logging.error(f"Failed to fetch products. Status code: {response.status_code}")
    return []

def format_product_message(product):
    """
    Format product details into a Telegram-friendly message.
    """
    name = product.get("nameEn", "No Name")
    price = float(product.get("sellPrice", 0))  # Selling price from CJ
    images = product.get("imageUrlList", [])
    product_id = product.get("productId", "Unknown")

    # Pricing formula
    market_price = price - 1500 if price >= 1500 else None
    if market_price is None:
        return None  # Skip the product if price condition is not met

    message = f"""
🛒 **{name}**  
💰 **Price:** ₹{market_price}  
🚚 **Non-Returnable**  

🔗 **[View Product](https://cjdropshipping.com/product-detail.html?productId={product_id})**
    """
    return message, images

def post_to_telegram():
    """
    Fetches products, formats them, and posts to Telegram.
    """
    products = fetch_products()
    if not products:
        logging.info("No products fetched.")
        return

    for product in products:
        message_data = format_product_message(product)
        if not message_data:
            continue

        message, images = message_data
        try:
            if images:
                bot.send_photo(chat_id=CHANNEL_ID, photo=images[0], caption=message, parse_mode="Markdown")
            else:
                bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
            time.sleep(2)  # Avoid spam rate limits
        except Exception as e:
            logging.error(f"Error posting to Telegram: {e}")

if __name__ == "__main__":
    logging.info("Starting TelBot...")
    post_to_telegram()
    logging.info("TelBot execution completed.")
