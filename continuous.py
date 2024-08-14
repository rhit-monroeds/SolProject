import requests
import time
import threading
import asyncio
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from telegram.error import TelegramError

app = Flask(__name__)

# TODO
# embed charts in page?
# get Telegram notifications
# have on public web
# track a specific wallet and sell when they do
# different version where keep a list of wallets that have transfered for
# past 24 hours and check them all for purchases in the past 1-4 hours

# Constants
CAT = "ACTIVITY_SPL_TRANSFER"
CPGS = 100
DAT = "ACTIVITY_SPL_TRANSFER"
DPGS = 100
NS = "So11111111111111111111111111111111111111111"
MST = 10
MSB = 9
TO = 24

# Globals
headers = {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MjMzNDc4ODIwMjcsImVtYWlsIjoiZGVhbm1vbnJvZTI4QGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTcyMzM0Nzg4Mn0.MeqTvUGP6HXZCC-jfQE5zJOVq0qRmnxQwbwLBDLFWGE"}
potential_insider_tokens = {}
token_info_cache = {}
insider_wallets = defaultdict(set)
latest_potential_insider_tokens = {}
latest_token_info_cache = {}
latest_insider_wallets = defaultdict(set)
notified_tokens = set()

lock = threading.Lock()
count = 0
last_update_time = 0
specific_time = 0

# wrapped Sol, WIF, POPCAT, MEW, PONKE, $michi, WOLF, BILLY, aura, FWOG, PGN, wDOG, MUMU, DOG, MOTHER, SCF, GINNAN, DADDY, USDC, DMAGA, NEIRO, $WIF, Jupiter, Jupiter, BTW, USDT, NOS, JitoSOL, NUGGIES, UWU, Jupiter, Neiro, mSOL, Bonk, RETARDIO
# WBTC, ATLAS, RENDER, DUKO, HNT
ignore = ["So11111111111111111111111111111111111111112", "21AErpiB8uSb94oQKRcwuHqyHF93njAxBSbdUrpupump", "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5", "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC", 
          "5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp", "Faf89929Ni9fbg4gmVZTca7eW6NFg877Jqn6MizT3Gvw", "3B5wuUrMEi5yATD7on46hKfej3pfmd7t1RKgrsN3pump", "DtR4D9FtVoTX2569gaL837ZgrB6wNjj6tkmnX9Rdk9B2", "A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump", 
          "2Vnei1LAmrBpbL8fNCiCpaYcQTCSodiE51wab6qaQJAq", "GYKmdfcUmZVrqfcH1g579BGjuzSRijj3LBuwv79rpump", "5LafQUrVco6o7KMz42eqVEJ9LW31StPyGjeeu5sKoMtA", "CATTzAwLyADd2ekzVjTjX8tVUBYfrozdkJBkutJggdB7", "3S8qX1MsMqRbiwKg2cQyx7nis1oHMgaCuc9c4VfvVdPN", 
          "GiG7Hr61RVm4CSUxJmgiCoySFQtdiwxtqf64MsRppump", "GinNabffZL4fUj9Vactxha74GDAW8kDPGaHqMtMzps2f", "4Cnk9EPnW5ixfLZatCPJjDB1PUtcRpVVgTQukm9epump", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "7D7BRcBYepfi77vxySapmeqRNN1wsBBxnFPJGbH5pump",
          "CTg3ZgYx79zrE1MteDVkmkcGniiFrK1hJ6yiabropump", "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4", "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", "4ytpZgVoNB66bFs6NRCUaAVsLdtYk2fHq4U92Jnjpump",
          "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7", "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn", "Ej6Lz2Cje5iRziDKnmfpd9Y3bpGe6HDQJGxVbxu4pump", "UwU8RVXB69Y6Dcju6cN2Qef6fykkq6UUNpB15rZku6Z",
          "jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v", "CTJf74cTo3cw8acFP1YXF3QpsQUUBGBjh2k2e8xsZ6UL", "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "6ogzHhzdrQr9Pgv6hZ2MNze7UrzBMAFyBBWUYp1Fhitx",
          "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh", "ATLASXmbPQxBUYbxPsV97usA3fPQYEqzQBUHgiFCUsXx", "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof", "HLptm5e6rTgh4EKgDpYFrnRHbjpkMyVdEeREEa2G7rf9", "hntyVP6YFm1Hg25TN9WGLqM12b8TQmcknKrdu1oxWux",
          "Hax9LTgsQkze1YFychnBLtFH8gYbQKtKfWKKg2SP6gdD"]

r_1 = "G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t"
r_2 = "DQ5JWbJyWdJeyBxZuuyu36sUBud6L6wo3aN1QC1bRmsR"
r_3 = "DQ5JWbJyWdJeyBxZuuyu36sUBud6L6wo3aN1QC1bRmsR"
cb_hot = "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE"
cb_1 = "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS"
cb_2 = "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm"
bbit = "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2"
binan_2 = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"
kuc = "BmFdpraQhkiDQE6SnfG5omcA1VwzqfXrwtNYBwWTymy6"
ws = [r_1, r_2, r_3, cb_hot, cb_1, cb_2, bbit, binan_2, kuc]

def central_check():
    # TODO these threads may be useless?
    with ThreadPoolExecutor(max_workers=3) as executor:
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
    return

def decentral_checkout(w):
    # TODO could make this call more specific ex: only transactions in the range of the time offset
    ac = "https://pro-api.solscan.io/v2.0/account/transfer?address=" + w + "&activity_type[]=" + DAT + "&page=1&page_size=" + str(DPGS)
    response = requests.get(ac, headers=headers)
    if not response:
        raise Exception(f"Non-success status code: {response.status_code}")
    data = response.json()["data"]
    # TODO gets rid of day traders, could check to see if wallet has sold and add it if not
    if len(data) > 99:
        return
    # reverse data
    data = data[::-1]
    # traverse data and look for transfers of Solana greater than 4.9
    tid = "n/a"
    for transaction in data:
        if transaction["token_address"] == NS and transaction["flow"] == "out" and transaction["amount"] / 10 ** transaction["token_decimals"] > MSB:
            tid = transaction["trans_id"]
        elif transaction["flow"] == "in" and transaction["trans_id"] == tid and transaction["token_address"] not in ignore:
            with lock:
                length = len(insider_wallets[transaction["token_address"]])
                insider_wallets[transaction["token_address"]].add(transaction["to_address"]) 
                if length < len(insider_wallets[transaction["token_address"]]):
                    potential_insider_tokens[transaction["token_address"]] = potential_insider_tokens.get(transaction["token_address"], 0) + 1
            if transaction["token_address"] not in token_info_cache:
                tac = "https://pro-api.solscan.io/v2.0/token/meta?address=" + transaction["token_address"]
                response = requests.get(tac, headers=headers)
                if not response:
                    raise Exception(f"Non-success status code: {response.status_code}")
                data = response.json()
                token_info_cache[transaction["token_address"]] = data.get("data", {})
            break
    return

async def send_telegram_message(message):
    bot_token = '7403847561:AAFFs7t6EQ_dQggI_YOGeKgz1d_ZewzGaZc'
    chat_id = '6478230687'
    
    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except TelegramError as e:
        print(f"Failed to send Telegram message: {e}")

def send_telegram_message_sync(message):
    asyncio.run(send_telegram_message(message))

def update_data():
    global latest_potential_insider_tokens, latest_insider_wallets, last_update_time, latest_token_info_cache, specific_time, notified_tokens
    start_time = time.time()
    central_check()
    end_time = time.time()
    print("Update completed in", end_time - start_time, "seconds")
    print(potential_insider_tokens)
    
    # Update the latest results
    latest_potential_insider_tokens = dict(potential_insider_tokens)
    latest_token_info_cache = dict(token_info_cache)
    latest_insider_wallets = {k: set(v) for k, v in insider_wallets.items()}

    last_update_time = int(time.time())
    specific_time = datetime.fromtimestamp(last_update_time)

    # Check for new tokens and send notifications
    for token, count in latest_potential_insider_tokens.items():
        if token not in notified_tokens and count > 1:
            token_info = latest_token_info_cache.get(token, {})
            symbol = token_info.get('symbol', 'Unknown')
            name = token_info.get('name', 'Unknown')
            dexscreener_link = f"https://dextools.io/app/en/solana/pair-explorer/{token}"
            message = (f"New token found: {symbol} ({name})\n"
                       f"Address: {token}\n"
                       f"Count: {count}\n"
                       f"DexScreener: {dexscreener_link}")            
            send_telegram_message_sync(message)
            notified_tokens.add(token)
    
    # Clear the temporary data for the next run
    potential_insider_tokens.clear()
    token_info_cache.clear()
    insider_wallets.clear()

# Set up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", minutes=10)
scheduler.start()

@app.route("/")
def display_data():
    found_tokens = dict(sorted(latest_potential_insider_tokens.items(), key=lambda item: item[1], reverse=True))
    html_content = """
    <html>
    <head>
        <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
                padding: 5px;
            }
        </style>
        <script>
        function checkForUpdates() {
            fetch('/last_update')
                .then(response => response.json())
                .then(data => {
                    if (data.last_update > window.lastUpdateTime) {
                        location.reload();
                    }
                });
        }
        
        window.lastUpdateTime = {{ last_update_time }};
        setInterval(checkForUpdates, 3000);  // Check every 30 seconds
        </script>
    </head>
    <body>
        <h1 style="text-align: center;">Data Output</h1>

        <h2>{{ specific_time }}</h2>
        
        <div style="margin-bottom: 20px;">
        {% for key, value in data.items() %}
            {% if value|int > 1 %}
                <table>
                    <tr>
                        <th>|</th>
                        <th>|</th>
                    </tr>
                    {% for prop, prop_value in token_info[key].items() %}
                        <tr>
                            <td>{{ prop }}</td>
                            <td>{{ prop_value }}</td>
                        </tr>
                    {% endfor %}
                    <tr>
                        <tr>
                            <td>Associated Wallets:</td>
                            <td>
                                {% for iw in iws[key] %}
                                    <span style="margin-right: 20px;">{{ iw }}</span>
                                {% endfor %}
                            </td>
                        </tr>
                </table>                
                

            {% endif %}
        {% endfor %}
        </div>
        
    </body>
    </html>
    """
    return render_template_string(html_content, data=found_tokens, token_info=latest_token_info_cache, iws=latest_insider_wallets, last_update_time=last_update_time, specific_time=specific_time)

@app.route("/last_update")
def last_update():
    return jsonify({"last_update": last_update_time})

if __name__ == "__main__":
    update_data()
    app.run(debug=False)