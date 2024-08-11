import requests
import time
from datetime import datetime, timedelta


# Constants
CEX_ACTIVITY_TYPE = "ACTIVITY_SPL_TRANSFER"
CEX_PG_SZ = 100
DEX_ACTIVITY_TYPE = "ACTIVITY_SPL_TRANSFER"
DEX_PG_SZ = 100
NATIVE_SOLANA = "So11111111111111111111111111111111111111111"
MIN_SOL = 9
TIME_OFFSET = 24

# Globals
headers = {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MjMzNDc4ODIwMjcsImVtYWlsIjoiZGVhbm1vbnJvZTI4QGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTcyMzM0Nzg4Mn0.MeqTvUGP6HXZCC-jfQE5zJOVq0qRmnxQwbwLBDLFWGE"}

# CEX Wallet
binance_2 = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"

def cex_checkout():
    print("checking " + binance_2)
    start_time = time.time()
    pg = 1
    count = 0
    valid_wallets = 0
    avg_call_time = 0
    while 1:
        api_call = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + binance_2 + "&activity_type[]=" + CEX_ACTIVITY_TYPE + "&token=" + NATIVE_SOLANA + "&amount[]=" + str(MIN_SOL) + "&block_time[]=" + str((datetime.now() - timedelta(hours=TIME_OFFSET)).timestamp()) + "&block_time[]=" + str((datetime.now()).timestamp()) + "flow=out&page=" + str(pg) + "&page_size=" + str(CEX_PG_SZ)
        pg += 1
        api_before = time.time()
        response = requests.get(api_call, headers=headers)
        api_after = time.time()
        if not response:
            raise Exception(f"Non-success status code: {response.status_code}")
        count += 1
        avg_call_time = avg_call_time + ((api_after - api_before) - avg_call_time) / count
        data = response.json()["data"]
        if len(data) == 0:
            break
        for transfer in data:
            if transfer["to_address"] != binance_2 and transfer["amount"] / 10**9 > MIN_SOL:
                valid_wallets += 1
    return [count, start_time, valid_wallets, avg_call_time]

vals = cex_checkout()
print(vals[0])
print(time.time() - vals[1])
print(vals[2])
print(vals[3])