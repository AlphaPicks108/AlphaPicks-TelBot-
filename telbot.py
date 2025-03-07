import os
import logging
import requests
import telegram
from telegram import InputMediaPhoto

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load Secrets
CJ_API_KEY = os.getenv("CJ_API_KEY")  # CJ Dropshipping API Key
TELEGRAM_BOT_TOKEN = os.getenv("TELBOT_TOKEN")  # Telegram Bot Token
TELEGRAM_CHANNEL_ID = "your_channel_id_here"  # Replace with actual channel ID

# API Endpoints
CJ_PRODUCT_LIST_URL = "https://developers.cjdropshipping.com/api2.0/v1/product/list"

# Initialize Telegram Bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


def fetch_products():
    """Fetches products from CJ Dropshipping API with enhanced debugging."""
    headers = {"CJ-Access-Token": CJ_API_KEY}
    params = {
        "pageNum": 1,
        "pageSize": 12,  # Increased from 5 to 12 as per the update
        "type": 1,
    }

    response = requests.get(CJ_PRODUCT_LIST_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        logging.info(f"CJ API Response: {data}")  # <-- Print full response for debugging

        if data.get("status") == 200 and "list" in data:
            return data["list"]
        else:
            logging.error(f"Error from CJ API: {data.get('message')}")
            return []
    else:
        logging.error(f"Failed to fetch products. HTTP {response.status_code}")
        return []


def send_to_telegram(products):
    """Formats and sends fetched products to the Telegram channel."""
    if not products:
        logging.info("No products fetched.")
        return

    for product in products:
        title = product.get("name", "No title")
        price = product.get("sellPrice", "N/A")
        link = product.get("detailUrl", "#")
        images = product.get("imageUrls", [])

        message = f"🛍 *{title}*\n💰 Price: {price} USD\n🔗 [View Product]({link})\n🚫 Non-Returnable"

        media_group = []
        if images:
            for img in images[:5]:  # Limit to 5 images
                media_group.append(InputMediaPhoto(media=img))

            bot.send_media_group(chat_id=TELEGRAM_CHANNEL_ID, media=media_group)
        
        bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode="Markdown")


def main():
    """Main function to fetch products and send to Telegram."""
    logging.info("Starting TelBot...")
    
    products = fetch_products()
    send_to_telegram(products)

    logging.info("TelBot execution completed.")


if __name__ == "__main__":
    main()
