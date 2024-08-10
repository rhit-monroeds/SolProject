import requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string
from collections import defaultdict

app = Flask(__name__)

# Constants
CEX_ACTIVITY_TYPE = "ACTIVITY_SPL_TRANSFER"
CEX_PG_SZ = 100
DEX_ACTIVITY_TYPE = "ACTIVITY_SPL_TRANSFER"
DEX_PG_SZ = 100
NATIVE_SOLANA = "So11111111111111111111111111111111111111111"
MIN_SOL = 10
TIME_OFFSET = 24

# Globals
headers = {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MjMxNzE0NTQ0MjgsImVtYWlsIjoiZGVhbm1vbnJvZTI4QGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTcyMzE3MTQ1NH0.CbKikRboPJ8jgkLPskpAOGpOQ2nuppiXyRcQ7oWln-8"}
potential_insider_tokens = {}
insider_wallets = defaultdict(list)

# tokens to ignore
# wrapped Sol, WIF, POPCAT, MEW, PONKE, $michi, WOLF, BILLY, aura, FWOG, PGN, wDOG, MUMU, DOG, MOTHER, SCF, GINNAN, DADDY, USDC, DMAGA, NEIRO, $WIF, Jupiter, Jupiter, BTW, USDT, NOS, JitoSOL
ignore = ["So11111111111111111111111111111111111111112", "21AErpiB8uSb94oQKRcwuHqyHF93njAxBSbdUrpupump", "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5", "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC", 
          "5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp", "Faf89929Ni9fbg4gmVZTca7eW6NFg877Jqn6MizT3Gvw", "3B5wuUrMEi5yATD7on46hKfej3pfmd7t1RKgrsN3pump", "DtR4D9FtVoTX2569gaL837ZgrB6wNjj6tkmnX9Rdk9B2", "A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump", 
          "2Vnei1LAmrBpbL8fNCiCpaYcQTCSodiE51wab6qaQJAq", "GYKmdfcUmZVrqfcH1g579BGjuzSRijj3LBuwv79rpump", "5LafQUrVco6o7KMz42eqVEJ9LW31StPyGjeeu5sKoMtA", "CATTzAwLyADd2ekzVjTjX8tVUBYfrozdkJBkutJggdB7", "3S8qX1MsMqRbiwKg2cQyx7nis1oHMgaCuc9c4VfvVdPN", 
          "GiG7Hr61RVm4CSUxJmgiCoySFQtdiwxtqf64MsRppump", "GinNabffZL4fUj9Vactxha74GDAW8kDPGaHqMtMzps2f", "4Cnk9EPnW5ixfLZatCPJjDB1PUtcRpVVgTQukm9epump", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "7D7BRcBYepfi77vxySapmeqRNN1wsBBxnFPJGbH5pump",
          "CTg3ZgYx79zrE1MteDVkmkcGniiFrK1hJ6yiabropump", "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", "4ytpZgVoNB66bFs6NRCUaAVsLdtYk2fHq4U92Jnjpump",
          "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7", "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn"]

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
        print("checking " + wallet)
        pg = 1
        while 1:
            # "https://pro-api.solscan.io/v2.0/account/transfer?address=5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9&activity_type[]=ACTIVITY_SPL_TRANSFER&token=So11111111111111111111111111111111111111111&amount[]=5&block_time[]=123&block_time[]=165441&flow=out&page=1&page_size=10"
            api_call = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + wallet + "&activity_type[]=" + CEX_ACTIVITY_TYPE + "&token=" + NATIVE_SOLANA + "&amount[]=" + str(MIN_SOL) + "&block_time[]=" + str((datetime.now() - timedelta(hours=TIME_OFFSET)).timestamp()) + "&block_time[]=" + str((datetime.now()).timestamp()) + "flow=out&page=" + str(pg) + "&page_size=" + str(CEX_PG_SZ)
            pg += 1
            response = requests.get(api_call, headers=headers)
            if not response:
                raise Exception(f"Non-success status code: {response.status_code}")
            data = response.json()["data"]
            if len(data) == 0:
                break
            # check for old data, dont delete this comment
            # if data[CEX_PG_SZ-1]["block_time"] < int((datetime.now() - timedelta(hours=12)).timestamp()):
            #     break
            for transfer in data:
                # can probably remove this since API call is specific
                if transfer["amount"] / 10 ** transfer["token_decimals"] > MIN_SOL:
                    wallet_checkout(transfer["to_address"], transfer["block_time"])
    return

# analyze the transfers of wallet until the desired block_time is reached
def wallet_checkout(wallet, check_until):
    # pg = 1
    # flag = 1
    # viewed_tokens = {}
    # while flag:
    api_call = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + wallet + "&activity_type[]=" + DEX_ACTIVITY_TYPE + "&block_time[]=" + str(check_until) + "&block_time[]=" + str((datetime.now()).timestamp()) +"&page=1&page_size=" + str(DEX_PG_SZ)
    # pg += 1
    response = requests.get(api_call, headers=headers)
    if not response:
        raise Exception(f"Non-success status code: {response.status_code}")
    data = response.json()["data"]
    # reverse data
    data = data[::-1]
    # traverse data and look for transfers of Solana greater than 4.9
    tid = "n/a"
    for transfer in data:
        if transfer["token_address"] == NATIVE_SOLANA and transfer["flow"] == "out" and transfer["amount"] / 10 ** transfer["token_decimals"] > (MIN_SOL - 0.1):
            tid = transfer["trans_id"]
        elif transfer["flow"] == "in" and transfer["trans_id"] == tid and transfer["token_address"] not in ignore:
            potential_insider_tokens[transfer["token_address"]] = potential_insider_tokens.get(transfer["token_address"], 0) + 1
            insider_wallets[transfer["token_address"]].append(transfer["to_address"]) 
            break
                # viewed_tokens[transfer["token_address"]] = viewed_tokens.get(transfer["token_address"], 0) + 1
    # flag it and look at next transaction which should be buying the token
    # can compare tx address to make sure it's a swap not 2 seperate transfers
    # if all looks good, save it in potential insider token array
    
        # if len(data) == 0:
        #     break
        # for transfer in data:
        #     big_buy = 0
        #     transaction_id = transfer["trans_id"]
        #     api_tx_call = "https://pro-api.solscan.io/v2.0/transaction/actions?tx=" + transaction_id
        #     tx_response = requests.get(api_tx_call, headers=headers)
        #     if not tx_response:
        #         raise Exception(f"Non-success status code: {tx_response.status_code}")
        #     tx = tx_response.json()["data"]
        #     if tx["block_time"] > check_until:
        #         swaps = tx["transfers"]
        #         for swap in swaps:
        #             if swap["transfer_type"] == DEX_ACTIVITY_TYPE:
        #                 if swap["token_address"] == NATIVE_SOLANA:
        #                     if swap["amount"] / 10 ** swap["decimals"] > 4.9:
        #                         big_buy = 1
        #                 elif big_buy == 1:
        #                     # made a big buy, now we're in the swap for the potential insider token     
        #                     if swap["token_address"] not in ignore and viewed_tokens.get(swap["token_address"], 0) == 0:
        #                         potential_insider_tokens[swap["token_address"]] = potential_insider_tokens.get(swap["token_address"], 0) + 1
        #                         viewed_tokens[swap["token_address"]] = viewed_tokens.get(swap["token_address"], 0) + 1
        #     else:
        #         flag = 0
        #         break
    return

if __name__ == "__main__":
    cex_checkout()
    print(potential_insider_tokens)
    # set up Flask to view data better
    @app.route("/")
    def display_data():
        output = dict(sorted(potential_insider_tokens.items(), key=lambda item: item[1], reverse=True))
        # Render the data as a pretty-printed JSON string
        html_content = """
        <html>
        <body>
            <h1 style="text-align: center;">Data Output</h1>
            
            <h2 style="text-align: center;">Potential Insider Tokens</h2>
            <div style="margin-bottom: 20px;">
            {% for key, value in data.items() %}
                <p>{{ key }}: {{ value }}</p>
                <p>{{ iw[key] }}</p>
            {% endfor %}
            </div>
            
        </body>
        </html>
        """
            # <h2 style="text-align: center;">Other Data Set</h2>
            # <pre style="white-space: pre-wrap; word-wrap: break-word; width: 90%; font-size: 16px;">
            # {}</pre>
        return render_template_string(html_content, data=output, iw=insider_wallets)
    app.run(debug=False)