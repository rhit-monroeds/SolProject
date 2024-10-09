import requests
import time
import threading
import asyncio
import json
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import ApplicationBuilder, CommandHandler

app = Flask(__name__)

# latest version but it breaks on second run

# TODO
# track a specific wallet and sell when they do
# different version where keep a list of wallets that have transfered for past 24 hours and check them all for purchases in the past 1-4 hours
# send telegram message to start/end remotely, will have to run perpetually and is just idle until the message is sent
# add a button that displays all the insider wallets of the token when you click it

# Constants
CAT = "ACTIVITY_SPL_TRANSFER"
CPGS = 100
DAT = "ACTIVITY_SPL_TRANSFER"
DPGS = 100
NS = "So11111111111111111111111111111111111111111"
WS = "So11111111111111111111111111111111111111112"
MST = 10
MSB = 9
TO = 24

# Globals
headers = {"token":"your-api-key"}
potential_insider_tokens = {}
token_info_cache = {}
insider_wallets = defaultdict(set)
latest_potential_insider_tokens = {}
latest_token_info_cache = {}
latest_insider_wallets = defaultdict(set)
notified_tokens = set()
previous_insider_wallet_counts = {}
ignore = []

lock = threading.Lock()
count = 0
last_update_time = 0
specific_time = 0

r_1 = "G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t"
r_2 = "DQ5JWbJyWdJeyBxZuuyu36sUBud6L6wo3aN1QC1bRmsR"
cb_hot = "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE"
cb_1 = "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS"
cb_2 = "2AQdpHJ2JpcEgPiATUXjQxA8QmafFegfQwSLWSprPicm"
bbit = "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2"
binan_2 = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"
kuc = "BmFdpraQhkiDQE6SnfG5omcA1VwzqfXrwtNYBwWTymy6"
okx = "5VCwKtCXgCJ6kit5FybXjvriW3xELsFDhYrPSqtJNmcD"
ws = [r_1, r_2, cb_hot, cb_1, cb_2, bbit, binan_2, kuc, okx]

async def add_token_to_ignore(update, context):
    if not context.args:
        await update.message.reply_text("Please provide a token address to add to the ignore list.")
        return

    token_address = context.args[0]
    
    if token_address in ignore:
        await update.message.reply_text(f"Token address {token_address} is already in the ignore list.")
    else:
        ignore.append(token_address)
        await update.message.reply_text(f"{token_address} has been added to the ignore list.")

    # Optional: Save the updated ignore list to a file
    save_ignore_list()

def save_ignore_list():
    with open('ignore_list.json', 'w') as f:
        json.dump(ignore, f)

def central_check():
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
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = []
                    for t in data:
                        if t["to_address"] not in ws:
                            futures.append(executor.submit(decentral_checkout, t["to_address"]))
    return

def decentral_checkout(w):
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
        if (transaction["token_address"] == NS or transaction["token_address"] == WS) and transaction["flow"] == "out" and transaction["amount"] / 10 ** transaction["token_decimals"] > MSB:
            tid = transaction["trans_id"] 
        elif transaction["flow"] == "in" and transaction["trans_id"] == tid and transaction["token_address"] not in ignore and transaction["amount"] / 10 ** transaction["token_decimals"] > 1:
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
    bot_token = 'your-telegram-bot'
    chat_id = 'your-telegram-id'
    
    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except TelegramError as e:
        print(f"Failed to send Telegram message: {e}")
    return bot

def send_telegram_message_sync(message):
    return asyncio.get_event_loop().run_until_complete(send_telegram_message(message))

def load_ignore_list():
    global ignore
    try:
        with open('ignore_list.json', 'r') as f:
            ignore = json.load(f)
    except FileNotFoundError:
        # if the file doesn't exist, use the default ignore list
        pass

def update_data():
    global latest_potential_insider_tokens, latest_insider_wallets, last_update_time, latest_token_info_cache, specific_time, notified_tokens, previous_insider_wallet_counts
    start_time = time.time()
    central_check()
    end_time = time.time()
    print("Update completed in", end_time - start_time, "seconds")
    print(potential_insider_tokens)
    
    # update the latest results
    latest_potential_insider_tokens = dict(potential_insider_tokens)
    latest_token_info_cache = dict(token_info_cache)
    latest_insider_wallets = {k: set(v) for k, v in insider_wallets.items()}

    last_update_time = int(time.time())
    specific_time = datetime.fromtimestamp(last_update_time)

    # check for new tokens and send notifications
    for token, count in latest_potential_insider_tokens.items():

        # check for increase in insider wallets
        current_iw_count = len(latest_insider_wallets.get(token, set()))
        previous_iw_count = previous_insider_wallet_counts.get(token, 0)

        if token not in notified_tokens and count > 1:
            send_token_notification(token, count)
            notified_tokens.add(token)
        elif token in notified_tokens and current_iw_count > previous_iw_count:
            send_iw_increase_notification(token, previous_iw_count, current_iw_count)
        
        # update the previous count for the next iteration
        previous_insider_wallet_counts[token] = current_iw_count
    
    # clear the temporary data for the next run
    potential_insider_tokens.clear()
    token_info_cache.clear()
    insider_wallets.clear()

def send_token_notification(token, count):
    token_info = latest_token_info_cache.get(token, {})
    symbol = token_info.get('symbol', 'Unknown')
    name = token_info.get('name', 'Unknown')
    dexscreener_link = f"https://dextools.io/app/en/solana/pair-explorer/{token}"
    message = (f"New token found: {symbol} ({name})\n"
               f"Address: {token}\n"
               f"Count: {count}\n"
               f"DexScreener: {dexscreener_link}")            
    send_telegram_message_sync(message)

def send_iw_increase_notification(token, previous_count, current_count):
    token_info = latest_token_info_cache.get(token, {})
    symbol = token_info.get('symbol', 'Unknown')
    name = token_info.get('name', 'Unknown')
    dexscreener_link = f"https://dextools.io/app/en/solana/pair-explorer/{token}"
    message = (f"Insider wallet increase for: {symbol} ({name})\n"
               f"Address: {token}\n"
               f"Previous count: {previous_count}\n"
               f"Current count: {current_count}\n"
               f"DexScreener: {dexscreener_link}")
    send_telegram_message_sync(message)

# set up the scheduler
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
    load_ignore_list()
    update_data()

    # set up the Telegram bot
    application = ApplicationBuilder().token('your-token').build()
    
    # add command handlers
    application.add_handler(CommandHandler("add", add_token_to_ignore))
    
    # start the bot
    application.run_polling()

    app.run(debug=False)