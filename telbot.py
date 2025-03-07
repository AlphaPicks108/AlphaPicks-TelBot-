import os
import requests
import logging
from telegram import Bot
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load secrets from environment variables
CJ_API_KEY = os.getenv("CJ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELBOT_TOKEN")

# Hardcoded Telegram Channel ID
TELEGRAM_CHANNEL_ID = "-1001234567890"  # Replace with your actual channel ID

# CJ API Endpoint for fetching product list
CJ_PRODUCT_LIST_URL = "https://developers.cjdropshipping.com/api2.0/v1/product/list"

# Fetch products from CJ API
def fetch_products():
    headers = {"CJ-Access-Token": CJ_API_KEY}
    params = {
        "pageNum": 1,  # Fetch first page
        "pageSize": 12,  # Increased from 5 to 12
        "type": 1,  # Normal products
    }

    response = requests.get(CJ_PRODUCT_LIST_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 200 and "list" in data:
            return data["list"]
        else:
            logging.error(f"Error from CJ API: {data.get('message')}")
            return []
    else:
        logging.error(f"Failed to fetch products. HTTP {response.status_code}")
        return []

# Send product details to Telegram channel
def send_to_telegram(product):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    product_name = product.get("name", "No Name")
    product_price = product.get("sellPrice", 0)
    product_images = product.get("image", [])
    
    message = f"🛍 *{product_name}*\n"
    message += f"💰 Price: {product_price} USD\n"
    message += f"🚫 Non-returnable\n\n"
    message += f"🔗 [View Product]({product.get('url', '#')})"

    # Send text message
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode="Markdown")

    # Send product images if available
    if product_images:
        for img in product_images[:3]:  # Send max 3 images per product
            bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=img)

# Main function
def main():
    logging.info("Starting TelBot...")
    products = fetch_products()

    if products:
        for product in products:
            send_to_telegram(product)
    else:
        logging.info("No products fetched.")

    logging.info("TelBot execution completed.")

if __name__ == "__main__":
    main()

