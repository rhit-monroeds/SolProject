import requests
import json
from datetime import datetime, timedelta
from flask import Flask, render_template_string
from collections import defaultdict

# Constants
MIN_SOL = 9

# Globals
potential_insider_tokens = {}
insider_wallets = defaultdict(list)
# Set the Solana RPC endpoint
solana_endpoint = 'https://nd-923-390-846.p2pify.com/39df60dcfd8e7e0dd597695da0d2d97d'

# solana_endpoint = 'https://go.getblock.io/ecd992c1da5a4a8dbe09b990b58281af'
# solana_endpoint = 'https://solana-mainnet.core.chainstack.com/9f3e3bae8b45fc1b63d8eebe29c3b12b'
# sender_address = 'ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ'

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


# before should start as no value so that it is the most recent block
# then it should update to the oldest transaction signature that was returned
#
# until should start as a transaction signature from ~24hr ago and stay there
def get_signatures_for_address(address, before=None):
    limit = 1000  # Max limit per request
    headers = {'Content-Type': 'application/json'}
    params = {
        "limit": limit,
    }
    if before:
        params["before"] = before

    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            address,
            params
        ]
    })
    response = requests.post(solana_endpoint, headers=headers, data=body)
    if not response:
        raise Exception(f"Non-success status code: {response.status_code}")
    return response.json().get('result', {})

def get_transaction_details(signature):
    headers = {'Content-Type': 'application/json'}
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            "jsonParsed"
        ]
    })
    response = requests.post(solana_endpoint, headers=headers, data=body)
    if not response:
        raise Exception(f"Non-success status code: {response.status_code}")
    return response.json().get('result', {})

def analyze_transactions(address):
    last_signature = None
    sol_transfers = []

    while True:
        signatures = get_signatures_for_address(address, last_signature)
        if not signatures:
            break  # No more transactions to fetch

        for signature_data in signatures:
            transaction_detail = get_transaction_details(signature_data['signature'])
            print("transaction detail")
            print(transaction_detail)
            transaction = transaction_detail.get('transaction', {})
            message = transaction.get('message', {})

            for instruction in message.get('instructions', []):
                if instruction.get('programId') == '11111111111111111111111111111111':  # Check for system program
                    parsed = instruction.get('parsed', {})
                    if parsed.get('type') == 'transfer':
                        info = parsed.get('info', {})
                        sols = info['lamports'] / 10**9
                        if sols > MIN_SOL:
                            sol_transfers.append({'recipient': info['destination'], 'amount': sols, 'signature': signature_data['signature']})
            
            last_signature = signature_data['signature']  # Update to fetch the next batch
            print("last signature")
            block_time = transaction_detail.get('blockTime')
            print(block_time)
            print(last_signature)

    return sol_transfers

# Running the analysis and printing the results
for wallet in wallets:
    results = analyze_transactions(wallet)
    for result in results:
        print(f"Recipient: {result['recipient']}, Amount: {result['amount']} SOLs, Signature: {result['signature']}")