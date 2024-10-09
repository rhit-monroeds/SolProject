import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Constants
CEX_PG_SZ = 100

# Globals
headers = {"token":"your-api-key"}

# CEX Wallet
binance_2 = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"

def fetch_page(page):
    api_call = f"https://pro-api.solscan.io/v2.0/account/transfer?address={binance_2}&page={page}&page_size={CEX_PG_SZ}"
    response = requests.get(api_call, headers=headers)
    if not response:
        raise Exception(f"Non-success status code: {response.status_code}")
    return response.json()

def cex_checkout():
    print("checking " + binance_2)
    start_time = time.time()
    count = 0
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for pg in range(1, 1000):
            futures.append(executor.submit(fetch_page, pg))
            count += 1
            if time.time() - start_time > 60:
                break
        results = [future.result() for future in futures]
    return [count, time.time() - start_time]

vals = cex_checkout()
print(vals[0])
print(vals[1])