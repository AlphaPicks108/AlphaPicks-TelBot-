import os
import requests
import time
import logging
from telegram import Bot

# Load Secrets
CJ_API_KEY = os.getenv("CJ_API_KEY")  # CJ Dropshipping API Key
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_TELBOT")  # TelBot Token
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # Telegram Channel ID

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# CJ API Endpoints
CJ_PRODUCT_LIST_URL = "https://developers.cjdropshipping.com/api2.0/v1/product/list"

# Pricing Formula
MIN_PROFIT = 1500  # Minimum profit threshold

def fetch_products(category_id, limit=5):
    """Fetch 5 products from CJ Dropshipping for a specific category"""
    headers = {"CJ-Access-Token": CJ_API_KEY}
    params = {
        "pageNum": 1,
        "pageSize": limit,
        "categoryId": category_id
    }
    response = requests.get(CJ_PRODUCT_LIST_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("list", [])
    else:
        logging.error(f"Error fetching products: {response.text}")
        return []

def calculate_price(cj_cost, market_price):
    """Calculate selling price using the pricing formula"""
    profit = market_price - cj_cost
    return market_price if profit >= MIN_PROFIT else None

def format_product_message(product):
    """Format product details for Telegram"""
    title = product["name"]
    images = product["imageList"]
    price = product["sellPrice"]
    url = product["url"]

    message = (
        f"📌 **{title}**\n"
        f"💰 **Price:** ₹{price}\n"
        f"🔗 [Buy Now]({url})\n"
        f"🚫 *Non-Returnable*"
    )
    return message, images

def post_to_telegram(product):
    """Post product details to the Telegram channel"""
    message, images = format_product_message(product)

    # Send product details
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode="Markdown")

    # Send images (Telegram only supports sending one image at a time with caption)
    if images:
        bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=images[0])

def main():
    """Fetch and post 5 products per category every 4 hours"""
    categories = ["12345", "67890"]  # Replace with actual CJ category IDs
    for category in categories:
        products = fetch_products(category)
        for product in products:
            price = calculate_price(product["sellPrice"], product["marketPrice"])
            if price:
                post_to_telegram(product)
            time.sleep(3)  # Avoid API spam
        time.sleep(5)  # Delay between categories

if __name__ == "__main__":
    main()
