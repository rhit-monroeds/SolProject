import requests
import time

# Constants
CEX_PG_SZ = 100

# Globals
headers = {"token":"your-api-key"}

# CEX Wallet
binance_2 = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"

def cex_checkout():
    print("checking " + binance_2)
    start_time = time.time()
    pg = 1
    count = 0
    while 1:
        api_call = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + binance_2 + "&page=" + str(pg) + "&page_size=" + str(CEX_PG_SZ)
        pg += 1
        response = requests.get(api_call, headers=headers)
        if not response:
            raise Exception(f"Non-success status code: {response.status_code}")
        count += 1
        if time.time() - start_time > 60:
            break
    return count

api_call_total = cex_checkout()
print(api_call_total)