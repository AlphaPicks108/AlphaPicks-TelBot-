import logging
import requests
import telebot
import os

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("CJ_API_URL")  # CJ API URL from environment variables
API_KEY = os.getenv("CJ_API_KEY")  # CJ API Key

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Function to fetch CJ products
def fetch_cj_products():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        response = requests.get(API_URL, headers=headers)
        response_json = response.json()

        if response_json["code"] == 200 and response_json.get("success"):
            product_list = response_json["data"]["list"] if "data" in response_json and "list" in response_json["data"] else []
            if product_list:
                logging.info(f"Successfully fetched {len(product_list)} products from CJ API.")
                return product_list
            else:
                logging.info("No products found in the CJ API response.")
                return []
        else:
            logging.error(f"Error from CJ API: {response_json.get('message', 'Unknown Error')}")
            return []
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return []

# Telegram command to fetch CJ products
@bot.message_handler(commands=["products"])
def send_products(message):
    products = fetch_cj_products()
    
    if products:
        response_text = "\n".join([f"{p.get('productNameEn', 'N/A')} - ${p.get('sellPrice', 'N/A')}" for p in products[:5]])
        bot.send_message(message.chat.id, f"🛒 Here are some CJ products:\n\n{response_text}")
    else:
        bot.send_message(message.chat.id, "No products found.")

# Start bot polling
if __name__ == "__main__":
    logging.info("Bot is running...")
    bot.polling()
