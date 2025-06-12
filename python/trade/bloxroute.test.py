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

    # Build Keypair
    secret = base58.b58decode(private_key_b58)
    wallet = Keypair.from_secret_key(secret)
    print(f"wallet: {wallet.public_key}")

    # Prepare the trading payload
    param = {
        "wallet_address": str(wallet.public_key),  # Your wallet pubkey
        "action": "buy",                           # "buy" or "sell"
        "mint": "",                                # token mint address
        "dex": "jupiter",                          # "pumpfun", "raydium", etc.
        "amount": 0.00001,                         # amount of SOL or tokens
        "slippage": 100,                           # percent slippage allowed
        "tip": 0.001,                              # priority fee
        "type": "bloxroute",                       # "jito" or "bloxroute"
    }

    # 1) Request an unsigned, partially-signed txn from SolanaPortal
    url_trade = "https://api.solanaportal.io/api/trading"
    resp = requests.post(url_trade, json=param)
    if resp.status_code != 200:
        print("Error fetching transaction:", resp.text)
        return

    # The API returns a base64-encoded VersionedTransaction
    txn_b64 = resp.json()
    txn_bytes = base64.b64decode(txn_b64)

    # 2) Deserialize & sign locally
    txn = VersionedTransaction.deserialize(txn_bytes)
    txn.sign([wallet])

    # 3) Send signed txn to the bloxroute endpoint
    signed_b64 = base64.b64encode(txn.serialize()).decode()
    blox_payload = {"encodedTxn": signed_b64}
    url_blox = "https://api.solanaportal.io/api/bloxroute"
    blox_resp = requests.post(url_blox, json=blox_payload)
    if blox_resp.status_code == 200:
        signature = blox_resp.json().get("signature")
        print("- txn succeed:", f"https://solscan.io/tx/{signature}")
    else:
        print("- txn failed, please check the parameters:", blox_resp.text)

if __name__ == "__main__":
    main()
