import requests
import json

# Set the Solana RPC endpoint
# solana_endpoint = 'https://go.getblock.io/ecd992c1da5a4a8dbe09b990b58281af'
# solana_endpoint = 'https://solana-mainnet.core.chainstack.com/9f3e3bae8b45fc1b63d8eebe29c3b12b'
solana_endpoint = 'https://nd-923-390-846.p2pify.com/39df60dcfd8e7e0dd597695da0d2d97d'
# Sender address to monitor
# sender_address = '4ofSuTsnhzQ9nSaN4kDxX7NGda67zJRZPyKRVZLGmek1'
sender_address = 'ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ'

def get_signatures_for_address(address, before=None):
    limit = 10  # Max limit per request
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
        print('a')
        signatures = get_signatures_for_address(address, last_signature)
        if not signatures:
            break  # No more transactions to fetch

        for signature_data in signatures:
            print('b')
            transaction_detail = get_transaction_details(signature_data['signature'])
            transaction = transaction_detail.get('transaction', {})
            message = transaction.get('message', {})

            for instruction in message.get('instructions', []):
                if instruction.get('programId') == '11111111111111111111111111111111':  # Check for system program
                    parsed = instruction.get('parsed', {})
                    if parsed.get('type') == 'transfer':
                        info = parsed.get('info', {})
                        sols = info['lamports'] / 10**9
                        sol_transfers.append({'recipient': info['destination'], 'amount': sols, 'signature': signature_data['signature']})
                        print(sols)
            
            last_signature = signature_data['signature']  # Update to fetch the next batch

    return sol_transfers

# Running the analysis and printing the results
results = analyze_transactions(sender_address)
for result in results:
    print(f"Recipient: {result['recipient']}, Amount: {result['amount']} SOLs, Signature: {result['signature']}")