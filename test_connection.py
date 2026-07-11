"""
Bitkub API Test Connection Script
ใช้สำหรับทดสอบการเชื่อมต่อ API ก่อนใช้งาน DCA Bot
"""

import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "https://api.bitkub.com"


def get_signature(api_secret: str, timestamp: int, method: str, path: str, payload: str = "") -> str:
    """Generate HMAC-SHA256 signature for Bitkub API"""
    message = f"{timestamp}{method}{path}{payload}"
    signature = hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature


def test_server_status():
    """Test 1: Check server status (public endpoint)"""
    print("\n" + "="*50)
    print("Test 1: Server Status")
    print("="*50)

    try:
        response = requests.get(f"{BASE_URL}/api/status")
        data = response.json()

        if response.status_code == 200:
            print("Status: OK")
            print(f"Response: {data}")
            return True
        else:
            print(f"Status: FAILED (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_server_time():
    """Test 2: Get server time (public endpoint)"""
    print("\n" + "="*50)
    print("Test 2: Server Time")
    print("="*50)

    try:
        response = requests.get(f"{BASE_URL}/api/v3/servertime")
        data = response.json()

        if response.status_code == 200:
            server_time = data
            local_time = int(time.time() * 1000)
            diff = abs(server_time - local_time)

            print(f"Server Time: {server_time}")
            print(f"Local Time: {local_time}")
            print(f"Time Difference: {diff} ms")

            if diff > 5000:
                print("WARNING: Time difference > 5 seconds. This may cause signature errors.")

            return True
        else:
            print(f"Status: FAILED (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_market_ticker():
    """Test 3: Get BTC/THB ticker (public endpoint)"""
    print("\n" + "="*50)
    print("Test 3: Market Ticker (BTC/THB)")
    print("="*50)

    try:
        # Get all tickers
        response = requests.get(f"{BASE_URL}/api/v3/market/ticker")
        data = response.json()

        if response.status_code == 200:
            ticker = None

            # Handle list response - find BTC ticker
            if isinstance(data, list):
                for item in data:
                    sym = item.get("symbol", "")
                    # Match THB_BTC or BTC_THB format
                    if sym in ["THB_BTC", "BTC_THB"] or "BTC" in sym:
                        ticker = item
                        break
            # Handle dict response
            elif isinstance(data, dict) and "THB_BTC" in data:
                ticker = data["THB_BTC"]

            if ticker:
                print(f"Symbol: {ticker.get('symbol', 'N/A')}")
                print(f"Last Price: {float(ticker.get('last', 0)):,.2f} THB")
                print(f"24h High: {float(ticker.get('high_24_hr', 0)):,.2f} THB")
                print(f"24h Low: {float(ticker.get('low_24_hr', 0)):,.2f} THB")
                print(f"24h Volume: {float(ticker.get('base_volume', 0)):,.4f} BTC")
                return True
            else:
                print(f"Status: FAILED - BTC ticker not found")
                if isinstance(data, list) and len(data) > 0:
                    symbols = [item.get("symbol") for item in data[:5]]
                    print(f"Available symbols (first 5): {symbols}")
                return False
        else:
            print(f"Status: FAILED (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_api_key():
    """Test 4: Test API Key with wallet endpoint (secure endpoint)"""
    print("\n" + "="*50)
    print("Test 4: API Key Authentication (Wallet)")
    print("="*50)

    api_key = os.getenv("BITKUB_API_KEY")
    api_secret = os.getenv("BITKUB_API_SECRET")

    if not api_key or not api_secret:
        print("ERROR: API Key or Secret not found in .env file")
        print("Please copy .env.example to .env and fill in your credentials")
        return False

    if api_key == "your_api_key_here" or api_secret == "your_api_secret_here":
        print("ERROR: Please replace placeholder values in .env with actual credentials")
        return False

    try:
        timestamp = int(time.time() * 1000)
        method = "POST"
        path = "/api/v3/market/wallet"
        payload = "{}"

        signature = get_signature(api_secret, timestamp, method, path, payload)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-BTK-APIKEY": api_key,
            "X-BTK-TIMESTAMP": str(timestamp),
            "X-BTK-SIGN": signature
        }

        response = requests.post(f"{BASE_URL}{path}", headers=headers, json={})
        data = response.json()

        if response.status_code == 200:
            error_code = data.get("error", 0)

            if error_code == 0:
                print("Status: OK - API Key is valid!")
                result = data.get("result", {})

                print("\nWallet Balances:")
                print("-" * 30)

                thb_balance = result.get("THB", 0)
                btc_balance = result.get("BTC", 0)

                print(f"THB: {thb_balance:,.2f}")
                print(f"BTC: {btc_balance:.8f}")

                # Show other non-zero balances
                for currency, balance in result.items():
                    if currency not in ["THB", "BTC"] and balance > 0:
                        print(f"{currency}: {balance}")

                return True
            else:
                error_messages = {
                    1: "Invalid JSON payload",
                    2: "Missing API Key",
                    3: "Invalid API Key",
                    6: "Missing/Invalid signature",
                    8: "Invalid timestamp",
                    52: "Invalid permission (check API key permissions)",
                }
                error_msg = error_messages.get(error_code, f"Unknown error code: {error_code}")
                print(f"Status: FAILED - {error_msg}")
                return False
        else:
            print(f"Status: FAILED (HTTP {response.status_code})")
            print(f"Response: {data}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def test_trading_permission():
    """Test 5: Check if API has trading permission"""
    print("\n" + "="*50)
    print("Test 5: Trading Permission Check")
    print("="*50)

    api_key = os.getenv("BITKUB_API_KEY")
    api_secret = os.getenv("BITKUB_API_SECRET")

    if not api_key or not api_secret:
        print("SKIPPED: No API credentials")
        return None

    try:
        timestamp = int(time.time() * 1000)
        method = "GET"
        path = "/api/v3/market/my-open-orders"
        query = "sym=btc_thb"

        message = f"{timestamp}{method}{path}?{query}"
        signature = hmac.new(
            api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-BTK-APIKEY": api_key,
            "X-BTK-TIMESTAMP": str(timestamp),
            "X-BTK-SIGN": signature
        }

        response = requests.get(f"{BASE_URL}{path}?{query}", headers=headers)
        data = response.json()

        error_code = data.get("error", 0)

        if error_code == 0:
            print("Status: OK - Trading permission verified!")
            print("Your API key can view orders.")
            return True
        elif error_code == 52:
            print("WARNING: API key does not have trading permission")
            print("Please enable 'Trade' permission in Bitkub API settings")
            return False
        else:
            print(f"Status: Error code {error_code}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("\n" + "#"*50)
    print("#" + " "*14 + "BITKUB API TEST" + " "*15 + "#")
    print("#"*50)

    results = {}

    # Run tests
    results["Server Status"] = test_server_status()
    results["Server Time"] = test_server_time()
    results["Market Ticker"] = test_market_ticker()
    results["API Key Auth"] = test_api_key()
    results["Trading Permission"] = test_trading_permission()

    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    all_passed = True
    for test_name, result in results.items():
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "PASSED"
        else:
            status = "FAILED"
            all_passed = False
        print(f"{test_name}: {status}")

    print("\n" + "-"*50)
    if all_passed:
        print("All tests passed! Your API is ready for DCA Bot.")
    else:
        print("Some tests failed. Please fix the issues before using DCA Bot.")

    print("-"*50 + "\n")


if __name__ == "__main__":
    main()
