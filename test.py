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
START_TEST = 1723035810
END_TEST = 1723122210

# Globals
headers = {"token":"your-api-key"}
potential_insider_tokens = {}
insider_wallets = defaultdict(list)

# tokens to ignore
# wrapped Sol, WIF, POPCAT, MEW, PONKE, $michi, WOLF, BILLY, aura, FWOG, PGN, wDOG, MUMU, DOG, MOTHER, SCF, GINNAN, DADDY, USDC, DMAGA, NEIRO, $WIF, Jupiter, Jupiter, BTW, USDT, NOS, JitoSOL, NUGGIES, UWU, Jupiter, Neiro, mSOL
ignore = ["So11111111111111111111111111111111111111112", "21AErpiB8uSb94oQKRcwuHqyHF93njAxBSbdUrpupump", "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5", "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC", 
          "5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp", "Faf89929Ni9fbg4gmVZTca7eW6NFg877Jqn6MizT3Gvw", "3B5wuUrMEi5yATD7on46hKfej3pfmd7t1RKgrsN3pump", "DtR4D9FtVoTX2569gaL837ZgrB6wNjj6tkmnX9Rdk9B2", "A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump", 
          "2Vnei1LAmrBpbL8fNCiCpaYcQTCSodiE51wab6qaQJAq", "GYKmdfcUmZVrqfcH1g579BGjuzSRijj3LBuwv79rpump", "5LafQUrVco6o7KMz42eqVEJ9LW31StPyGjeeu5sKoMtA", "CATTzAwLyADd2ekzVjTjX8tVUBYfrozdkJBkutJggdB7", "3S8qX1MsMqRbiwKg2cQyx7nis1oHMgaCuc9c4VfvVdPN", 
          "GiG7Hr61RVm4CSUxJmgiCoySFQtdiwxtqf64MsRppump", "GinNabffZL4fUj9Vactxha74GDAW8kDPGaHqMtMzps2f", "4Cnk9EPnW5ixfLZatCPJjDB1PUtcRpVVgTQukm9epump", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "7D7BRcBYepfi77vxySapmeqRNN1wsBBxnFPJGbH5pump",
          "CTg3ZgYx79zrE1MteDVkmkcGniiFrK1hJ6yiabropump", "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", "4ytpZgVoNB66bFs6NRCUaAVsLdtYk2fHq4U92Jnjpump",
          "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7", "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn", "Ej6Lz2Cje5iRziDKnmfpd9Y3bpGe6HDQJGxVbxu4pump", "UwU8RVXB69Y6Dcju6cN2Qef6fykkq6UUNpB15rZku6Z",
          "jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v", "CTJf74cTo3cw8acFP1YXF3QpsQUUBGBjh2k2e8xsZ6UL", "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So"]

# CEX Wallets
random_1 = "G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t"
random_2 = "DQ5JWbJyWdJeyBxZuuyu36sUBud6L6wo3aN1QC1bRmsR"
cb_hot = "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE"
cb_1 = "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS"
cb_2 = "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm"
bybit = "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2"
binance_2 = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"
kucoin = "BmFdpraQhkiDQE6SnfG5omcA1VwzqfXrwtNYBwWTymy6"
wallets = [random_1, random_2, cb_hot, cb_1, cb_2, bybit, binance_2, kucoin]

def cex_checkout():
    for wallet in wallets:
        print("checking " + wallet)
        pg = 1
        while 1:
            api_call = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + wallet + "&activity_type[]=" + CEX_ACTIVITY_TYPE + "&token=" + NATIVE_SOLANA + "&amount[]=" + str(MIN_SOL) + "&block_time[]=" + str(START_TEST) + "&block_time[]=" + str(END_TEST) + "flow=out&page=" + str(pg) + "&page_size=" + str(CEX_PG_SZ)
            pg += 1
            response = requests.get(api_call, headers=headers)
            if not response:
                raise Exception(f"Non-success status code: {response.status_code}")
            data = response.json()["data"]
            if len(data) == 0:
                break
            for transfer in data:
                if transfer["to_address"] not in wallets and transfer["amount"] / 10 ** transfer["token_decimals"] > MIN_SOL:
                    wallet_checkout(transfer["to_address"])
    return

# analyze the transfers of wallet until the desired block_time is reached
def wallet_checkout(wallet):
    api_call = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + wallet + "&activity_type[]=" + DEX_ACTIVITY_TYPE + "&block_time[]=" + str(START_TEST) + "&block_time[]=" + str(END_TEST) + "&page=1&page_size=" + str(DEX_PG_SZ)
    response = requests.get(api_call, headers=headers)
    if not response:
        raise Exception(f"Non-success status code: {response.status_code}")
    data = response.json()["data"]
    if len(data) > 50:
        return
    data = data[::-1]
    tid = "n/a"
    for transfer in data:
        if transfer["token_address"] == NATIVE_SOLANA and transfer["flow"] == "out" and transfer["amount"] / 10 ** transfer["token_decimals"] > (MIN_SOL - 0.1):
            tid = transfer["trans_id"]
        elif transfer["flow"] == "in" and transfer["trans_id"] == tid and transfer["token_address"] not in ignore:
            potential_insider_tokens[transfer["token_address"]] = potential_insider_tokens.get(transfer["token_address"], 0) + 1
            insider_wallets[transfer["token_address"]].append(transfer["to_address"]) 
            break
    return

if __name__ == "__main__":
    cex_checkout()
    print(potential_insider_tokens)
    @app.route("/")
    def display_data():
        output = dict(sorted(potential_insider_tokens.items(), key=lambda item: item[1], reverse=True))
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
        return render_template_string(html_content, data=output, iw=insider_wallets)
    app.run(debug=False)