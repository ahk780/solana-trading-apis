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

    # Decode and create Keypair
    secret = base58.b58decode(private_key_b58)
    wallet = Keypair.from_secret_key(secret)
    print(f"wallet: {wallet.public_key}")

    # Build the trading request payload
    param = {
        "wallet_address": str(wallet.public_key),
        "action": "sell",       # "buy" or "sell"
        "dex": "pumpfun",       # DEX name
        "mint": "",             # token mint address
        "amount": 355486.039918,
        "slippage": 20,
        "tip": 0.0005,
        "type": "jito",         # "jito" or "bloxroute"
    }

    # 1) Fetch the partially-signed transaction from SolanaPortal
    url = "https://api.solanaportal.io/api/trading"
    resp = requests.post(url, json=param)
    if resp.status_code != 200:
        print("Error fetching transaction:", resp.text)
        return

    # The API returns a base64-encoded VersionedTransaction
    txn_b64 = resp.json()
    txn_bytes = base64.b64decode(txn_b64)

    # 2) Deserialize, sign, and re-serialize
    txn = VersionedTransaction.deserialize(txn_bytes)
    txn.sign([wallet])
    signed_txn = txn.serialize()
    signed_b58 = base58.b58encode(signed_txn).decode()

    # 3) Send the signed transaction to Jito’s RPC endpoint
    jito_url = "https://tokyo.mainnet.block-engine.jito.wtf/api/v1/transactions"
    jito_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendTransaction",
        "params": [signed_b58],
    }
    jito_resp = requests.post(jito_url, json=jito_payload)
    if jito_resp.status_code == 200:
        signature = jito_resp.json().get("result")
        print("- txn succeed:", f"https://solscan.io/tx/{signature}")
    else:
        print("- txn failed, please check the parameters:", jito_resp.text)

if __name__ == "__main__":
    main()
