#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import base64
import base58
import requests
from solana.keypair import Keypair
from solana.transaction import VersionedTransaction

def main():
    # Load PRIVATE_KEY from .env
    load_dotenv()
    private_key_b58 = os.getenv("PRIVATE_KEY")
    if not private_key_b58:
        raise EnvironmentError("Missing PRIVATE_KEY in environment")

    # Build your Solana wallet Keypair
    secret = base58.b58decode(private_key_b58)
    wallet = Keypair.from_secret_key(secret)
    print(f"wallet: {wallet.public_key}")

    # Prepare the create-pool payload
    param = {
        "market_id":    "",               # your pool market ID
        "wallet_address": str(wallet.public_key),
        "mint":          "",              # token mint address
        "tokenAmount":  1_000_000,        # amount of tokens to deposit
        "solAmount":    0.1,              # amount of SOL to deposit
        # Optional: start time in milliseconds since epoch
        # "startTime":    int((time.time() + 2*60*60) * 1000),
        "tip":          0.00001,          # priority fee
    }

    # 1) Request the unsigned pool-creation txn
    url = "https://api.solanaportal.io/api/create/pool"
    resp = requests.post(url, json=param)
    if resp.status_code != 200:
        print("Error generating pool-creation txn:", resp.text)
        return

    # 2) Deserialize & sign locally
    txn_b64   = resp.json()  # base64-encoded VersionedTransaction
    txn_bytes = base64.b64decode(txn_b64)
    txn       = VersionedTransaction.deserialize(txn_bytes)
    txn.sign([wallet])

    # 3) Re-serialize and base58-encode
    signed_b58 = base58.b58encode(txn.serialize()).decode()

    # 4) Send it via Jito RPC
    jito_url = "https://tokyo.mainnet.block-engine.jito.wtf/api/v1/transactions"
    jito_payload = {
        "jsonrpc": "2.0",
        "id":      1,
        "method":  "sendTransaction",
        "params":  [signed_b58],
    }
    jito_resp = requests.post(jito_url, json=jito_payload)
    if jito_resp.status_code == 200:
        signature = jito_resp.json().get("result")
        print("- txn succeed:", f"https://solscan.io/tx/{signature}")
    else:
        print("- txn failed, please check the parameters:", jito_resp.text)

if __name__ == "__main__":
    main()
