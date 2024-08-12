import requests
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template_string
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Constants
CAT = "ACTIVITY_SPL_TRANSFER"
CPGS = 100
DAT = "ACTIVITY_SPL_TRANSFER"
DPGS = 100
NS = "So11111111111111111111111111111111111111111"
MST = 10
MSB = 9
TO = 2

# Globals
headers = {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MjMzNDc4ODIwMjcsImVtYWlsIjoiZGVhbm1vbnJvZTI4QGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTcyMzM0Nzg4Mn0.MeqTvUGP6HXZCC-jfQE5zJOVq0qRmnxQwbwLBDLFWGE"}
pit = {}
iw = defaultdict(set)
lock = threading.Lock()

# wrapped Sol, WIF, POPCAT, MEW, PONKE, $michi, WOLF, BILLY, aura, FWOG, PGN, wDOG, MUMU, DOG, MOTHER, SCF, GINNAN, DADDY, USDC, DMAGA, NEIRO, $WIF, Jupiter, Jupiter, BTW, USDT, NOS, JitoSOL, NUGGIES, UWU, Jupiter, Neiro, mSOL, Bonk, RETARDIO
# WBTC, ATLAS
ignore = ["So11111111111111111111111111111111111111112", "21AErpiB8uSb94oQKRcwuHqyHF93njAxBSbdUrpupump", "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5", "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC", 
          "5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp", "Faf89929Ni9fbg4gmVZTca7eW6NFg877Jqn6MizT3Gvw", "3B5wuUrMEi5yATD7on46hKfej3pfmd7t1RKgrsN3pump", "DtR4D9FtVoTX2569gaL837ZgrB6wNjj6tkmnX9Rdk9B2", "A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump", 
          "2Vnei1LAmrBpbL8fNCiCpaYcQTCSodiE51wab6qaQJAq", "GYKmdfcUmZVrqfcH1g579BGjuzSRijj3LBuwv79rpump", "5LafQUrVco6o7KMz42eqVEJ9LW31StPyGjeeu5sKoMtA", "CATTzAwLyADd2ekzVjTjX8tVUBYfrozdkJBkutJggdB7", "3S8qX1MsMqRbiwKg2cQyx7nis1oHMgaCuc9c4VfvVdPN", 
          "GiG7Hr61RVm4CSUxJmgiCoySFQtdiwxtqf64MsRppump", "GinNabffZL4fUj9Vactxha74GDAW8kDPGaHqMtMzps2f", "4Cnk9EPnW5ixfLZatCPJjDB1PUtcRpVVgTQukm9epump", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "7D7BRcBYepfi77vxySapmeqRNN1wsBBxnFPJGbH5pump",
          "CTg3ZgYx79zrE1MteDVkmkcGniiFrK1hJ6yiabropump", "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", "4ytpZgVoNB66bFs6NRCUaAVsLdtYk2fHq4U92Jnjpump",
          "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7", "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn", "Ej6Lz2Cje5iRziDKnmfpd9Y3bpGe6HDQJGxVbxu4pump", "UwU8RVXB69Y6Dcju6cN2Qef6fykkq6UUNpB15rZku6Z",
          "jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v", "CTJf74cTo3cw8acFP1YXF3QpsQUUBGBjh2k2e8xsZ6UL", "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "6ogzHhzdrQr9Pgv6hZ2MNze7UrzBMAFyBBWUYp1Fhitx",
          "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh", "ATLASXmbPQxBUYbxPsV97usA3fPQYEqzQBUHgiFCUsXx"]

r_1 = "G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t"
r_2 = "DQ5JWbJyWdJeyBxZuuyu36sUBud6L6wo3aN1QC1bRmsR"
cb_hot = "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE"
cb_1 = "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS"
cb_2 = "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm"
bbit = "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2"
binan_2 = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"
kuc = "BmFdpraQhkiDQE6SnfG5omcA1VwzqfXrwtNYBwWTymy6"
ws = [r_1, r_2, cb_hot, cb_1, cb_2, bbit, binan_2, kuc]

def central_check():
    # these threads may be useless?
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for w in ws:
            print("checking " + w)
            pg = 1
            while 1:
                ac = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + w + "&activity_type[]=" + CAT + "&token=" + NS + "&amount[]=" + str(MST) + "&block_time[]=" + str((datetime.now() - timedelta(hours=TO)).timestamp()) + "&block_time[]=" + str((datetime.now()).timestamp()) + "flow=out&page=" + str(pg) + "&page_size=" + str(CPGS)
                pg += 1
                response = requests.get(ac, headers=headers)
                if not response:
                    raise Exception(f"Non-success status code: {response.status_code}")
                data = response.json()["data"]
                if len(data) == 0:
                    break
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = []
                    for t in data:
                        if t["to_address"] not in ws:
                            futures.append(executor.submit(decentral_checkout, t["to_address"]))
                    # results = [future.result() for future in futures]
        # results = [future.result() for future in futures]
    return

def decentral_checkout(w):
    # could make this call more specific ex: only transactions in the range of the time offset
    ac = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + w + "&activity_type[]=" + DAT + "&page=1&page_size=" + str(DPGS)
    response = requests.get(ac, headers=headers)
    if not response:
        raise Exception(f"Non-success status code: {response.status_code}")
    data = response.json()["data"]
    # gets rid of day traders, could check to see if wallet has sold and add it if not
    if len(data) > 99:
        return
    # reverse data
    data = data[::-1]
    # traverse data and look for transfers of Solana greater than 4.9
    tid = "n/a"
    for t in data:
        if t["token_address"] == NS and t["flow"] == "out" and t["amount"] / 10 ** t["token_decimals"] > MSB:
            tid = t["trans_id"]
        elif t["flow"] == "in" and t["trans_id"] == tid and t["token_address"] not in ignore:
            with lock:
                length = len(iw[t["token_address"]])
                iw[t["token_address"]].add(t["to_address"]) 
                if length < len(iw[t["token_address"]]):
                    pit[t["token_address"]] = pit.get(t["token_address"], 0) + 1
            break
    return

if __name__ == "__main__":
    start_time = time.time()
    central_check()
    end_time = time.time()
    print(pit)
    print(end_time - start_time)
    # set up Flask to view data better
    @app.route("/")
    def display_data():
        output = dict(sorted(pit.items(), key=lambda item: item[1], reverse=True))
        # Render the data as a pretty-printed JSON string
        html_content = """
        <html>
        <body>
            <h1 style="text-align: center;">Data Output</h1>
            
            <div style="margin-bottom: 20px;">
            {% for key, value in data.items() %}
                {% if value|int > 1 %}
                    <p>{{ key }}: {{ value }}</p>
                    {% for iw in iws[key] %}
                        <span style="margin-right: 20px;">{{ iw }}</span>
                    {% endfor %}
                {% endif %}
            {% endfor %}
            </div>
            
        </body>
        </html>
        """
        return render_template_string(html_content, data=output, iws=iw)
    app.run(debug=False)