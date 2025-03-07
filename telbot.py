import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_cj_products(api_url, headers):
    try:
        response = requests.get(api_url, headers=headers)
        response_json = response.json()

        # Check if API call was successful
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

# Run the function
API_URL = "https://your-cj-api-url.com"  # Change this after the first run
HEADERS = {"Authorization": "Bearer YOUR_API_KEY"}  # Change this after the first run

products = fetch_cj_products(API_URL, HEADERS)
if products:
    for product in products:
        print(f"Product Name: {product.get('productNameEn', 'N/A')}, Price: {product.get('sellPrice', 'N/A')}")
else:
    print("No products available.")
