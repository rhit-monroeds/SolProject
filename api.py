import requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string

app = Flask(__name__)

# Constants
CEX_ACTIVITY_TYPE = "ACTIVITY_SPL_TRANSFER"
CEX_PG_SZ = 100
NATIVE_SOLANA = "So11111111111111111111111111111111111111111"

# Globals
twenty_four_hours_ago_timestamp = int((datetime.now() - timedelta(hours=24)).timestamp())
headers = {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MjMxNzE0NTQ0MjgsImVtYWlsIjoiZGVhbm1vbnJvZTI4QGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTcyMzE3MTQ1NH0.CbKikRboPJ8jgkLPskpAOGpOQ2nuppiXyRcQ7oWln-8"}

# tokens to ignore
ignore = []

# CEX Wallets
random_1 = "G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t"
random_2 = "DQ5JWbJyWdJeyBxZuuyu36sUBud6L6wo3aN1QC1bRmsR"
cb_hot = "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE"
cb_1 = "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS"
bybit = "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2"
binance_2 = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"
wallets = [random_1, random_2, cb_hot, cb_1, bybit, binance_2]


# get transfers from random_1 which are SPL transfers
# of native Sol and are outflows
# url = "https://pro-api.solscan.io/v2.0/account/transfer?address=G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t&activity_type[]=ACTIVITY_SPL_TRANSFER&token=So11111111111111111111111111111111111111111&flow=out&page=1&page_size=10" 

def cex_checkout():
    for wallet in wallets:
        pg = 1
        while 1:
            api_call = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + wallet + "&activity_type[]=" + CEX_ACTIVITY_TYPE + "&token=" + NATIVE_SOLANA + "&flow=out&page=" + str(pg) + "&page_size=" + str(CEX_PG_SZ)
            pg += 1
            response = requests.get(api_call, headers=headers)
            if not response:
                raise Exception(f"Non-success status code: {response.status_code}")
            data = response.json()["data"]
            if data[CEX_PG_SZ-1]["block_time"] < twenty_four_hours_ago_timestamp:
                #print("data is now older than 24 hrs")
                #print(data[CEX_PG_SZ-1])
                break
            # we have data < 24 hrs old
            for transfer in data:
                if transfer["amount"] / 10 ** transfer["token_decimals"] > 5:
                    wallet_checkout(transfer["to_address"], transfer["block_time"])
    return

# analyze the transfers of wallet until the desired block_time is reached
def wallet_checkout(wallet, check_until):
    print(wallet)
    return

def main():
    cex_checkout()

    # set up Flask to view data better
    @app.route("/")
    def display_data():
        data = {
            "hi": 1,
        }
        # Render the data as a pretty-printed JSON string
        html_content = "<html><body><h1>Data Output</h1><pre>{}</pre></body></html>".format(data)
        return render_template_string(html_content)

    if __name__ == "__main__":
        app.run(debug=True)

main()

