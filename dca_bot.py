"""
Bitkub DCA Bot - Daily Bitcoin DCA
"""

import os
import time
import hmac
import hashlib
import requests
import schedule
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "https://api.bitkub.com"
API_KEY = os.getenv("BITKUB_API_KEY")
API_SECRET = os.getenv("BITKUB_API_SECRET")
DCA_AMOUNT = float(os.getenv("DCA_AMOUNT_THB", 100))
DCA_TIME = os.getenv("DCA_TIME", "09:00")
SYMBOL = os.getenv("SYMBOL", "btc_thb").lower()

# Get script directory for log file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, 'dca_bot.log')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_signature(timestamp: int, method: str, path: str, payload: str = "") -> str:
    """Generate HMAC-SHA256 signature for Bitkub API"""
    message = f"{timestamp}{method}{path}{payload}"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature


def get_headers(timestamp: int, signature: str) -> dict:
    """Get headers for authenticated requests"""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-BTK-APIKEY": API_KEY,
        "X-BTK-TIMESTAMP": str(timestamp),
        "X-BTK-SIGN": signature
    }


def get_wallet_balance() -> dict:
    """Get wallet balance"""
    timestamp = int(time.time() * 1000)
    method = "POST"
    path = "/api/v3/market/wallet"
    payload = "{}"

    signature = get_signature(timestamp, method, path, payload)
    headers = get_headers(timestamp, signature)

    response = requests.post(f"{BASE_URL}{path}", headers=headers, json={})
    return response.json()


def get_ticker() -> dict:
    """Get current ticker price for BTC"""
    response = requests.get(f"{BASE_URL}/api/v3/market/ticker")
    data = response.json()

    # Handle list response
    if isinstance(data, list):
        for item in data:
            sym = item.get("symbol", "")
            if "BTC" in sym:
                return {"THB_BTC": item}
    # Handle dict response
    elif isinstance(data, dict):
        return data
    return {}


def place_market_buy_order(amount_thb: float) -> dict:
    """
    Place a market buy order for Bitcoin
    amount_thb: Amount in THB to spend
    """
    timestamp = int(time.time() * 1000)
    method = "POST"
    path = "/api/v3/market/place-bid"

    # Payload for market order (use lowercase format like btc_thb)
    payload_dict = {
        "sym": SYMBOL,
        "amt": amount_thb,
        "rat": 0,  # 0 for market order
        "typ": "market"
    }

    import json
    payload = json.dumps(payload_dict, separators=(',', ':'))

    signature = get_signature(timestamp, method, path, payload)
    headers = get_headers(timestamp, signature)

    response = requests.post(f"{BASE_URL}{path}", headers=headers, data=payload)
    return response.json()


def execute_dca():
    """Execute DCA buy order"""
    logger.info("="*50)
    logger.info("Starting DCA execution...")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check wallet balance
    logger.info("Checking wallet balance...")
    wallet = get_wallet_balance()

    if wallet.get("error", 1) != 0:
        logger.error(f"Failed to get wallet balance: {wallet}")
        return

    thb_balance = wallet.get("result", {}).get("THB", 0)
    logger.info(f"THB Balance: {thb_balance:,.2f}")

    if thb_balance < DCA_AMOUNT:
        logger.warning(f"Insufficient balance! Need {DCA_AMOUNT:,.2f} THB but only have {thb_balance:,.2f} THB")
        return

    # Get current BTC price
    ticker = get_ticker()
    if "THB_BTC" in ticker:
        current_price = float(ticker["THB_BTC"].get("last", 0))
        logger.info(f"Current BTC Price: {current_price:,.2f} THB")

    # Place market buy order
    logger.info(f"Placing market buy order for {DCA_AMOUNT:,.2f} THB...")
    result = place_market_buy_order(DCA_AMOUNT)

    if result.get("error", 1) == 0:
        order_result = result.get("result", {})
        logger.info("Order placed successfully!")
        logger.info(f"Order ID: {order_result.get('id', 'N/A')}")
        logger.info(f"Amount spent: {order_result.get('amt', 'N/A')} THB")
        logger.info(f"BTC received: {order_result.get('rec', 'N/A')}")
        logger.info(f"Fee: {order_result.get('fee', 'N/A')} THB")
    else:
        error_code = result.get("error", "Unknown")
        error_messages = {
            1: "Invalid JSON payload",
            3: "Invalid API key",
            6: "Missing/Invalid signature",
            11: "Invalid symbol",
            12: "Invalid amount",
            18: "Insufficient balance",
            52: "Invalid permission",
        }
        error_msg = error_messages.get(error_code, f"Error code: {error_code}")
        logger.error(f"Order failed: {error_msg}")
        logger.error(f"Full response: {result}")

    logger.info("="*50)


def validate_config():
    """Validate configuration before starting"""
    errors = []

    if not API_KEY or API_KEY == "your_api_key_here":
        errors.append("BITKUB_API_KEY is not set")

    if not API_SECRET or API_SECRET == "your_api_secret_here":
        errors.append("BITKUB_API_SECRET is not set")

    if DCA_AMOUNT < 10:
        errors.append("DCA_AMOUNT_THB must be at least 10 THB")

    try:
        time_parts = DCA_TIME.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError()
    except (ValueError, IndexError):
        errors.append("DCA_TIME must be in HH:MM format (e.g., 09:00)")

    return errors


def main():
    print("\n" + "#"*50)
    print("#" + " "*12 + "BITKUB DCA BOT" + " "*14 + "#")
    print("#"*50)

    # Validate configuration
    errors = validate_config()
    if errors:
        print("\nConfiguration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the errors in .env file and try again.")
        return

    # Show configuration
    print(f"\nConfiguration:")
    print(f"  - Symbol: {SYMBOL.upper()}")
    print(f"  - DCA Amount: {DCA_AMOUNT:,.2f} THB")
    print(f"  - DCA Time: {DCA_TIME} (Thailand Time)")
    print(f"  - API Key: {API_KEY[:8]}...{API_KEY[-4:]}")

    # Test connection first
    print("\nTesting API connection...")
    wallet = get_wallet_balance()

    if wallet.get("error", 1) != 0:
        print(f"ERROR: Failed to connect to API: {wallet}")
        print("Please run test_connection.py first to diagnose the issue.")
        return

    thb_balance = wallet.get("result", {}).get("THB", 0)
    btc_balance = wallet.get("result", {}).get("BTC", 0)

    print(f"API connection successful!")
    print(f"  - THB Balance: {thb_balance:,.2f}")
    print(f"  - BTC Balance: {btc_balance:.8f}")

    # Schedule DCA
    schedule.every().day.at(DCA_TIME).do(execute_dca)

    print(f"\nDCA Bot started!")
    print(f"Next DCA scheduled at: {DCA_TIME}")
    print("Press Ctrl+C to stop\n")

    logger.info(f"DCA Bot started. Scheduled at {DCA_TIME} daily.")
    logger.info(f"Amount: {DCA_AMOUNT} THB, Symbol: {SYMBOL}")

    # Run scheduler
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nDCA Bot stopped.")
        logger.info("DCA Bot stopped by user.")


if __name__ == "__main__":
    main()
