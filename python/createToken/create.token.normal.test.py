#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import base64
import base58
import requests
from solana.keypair import Keypair
from solana.transaction import VersionedTransaction

def main():
    # Load your PRIVATE_KEY from .env
    load_dotenv()
    private_key_b58 = os.getenv("PRIVATE_KEY")
    if not private_key_b58:
        raise EnvironmentError("Missing PRIVATE_KEY in environment")

    # Build your Solana wallet Keypair
    secret = base58.b58decode(private_key_b58)
    wallet = Keypair.from_secret_key(secret)
    print(f"wallet: {wallet.public_key}")

    # 1) Upload metadata + image to IPFS via SolanaPortal
    url_create = "https://api.solanaportal.io/api/create/token/normal"

    # Prepare multipart form data
    files = {
        "image": open("./zz.png", "rb")
    }
    data = {
        "wallet_address": str(wallet.public_key),
        "name": "test",
        "symbol": "TEST",
        "decimals": "6",
        "total_supply": "1000000",
        "sellerFeeBasisPoints": "0",
        "description": "This is an example token created via SolanaPortal.AI",
        "twitter": "https://x.com/solana",
        "telegram": "https://x.com/solana",
        "website": "https://solanaportal.ai",
    }

    resp = requests.post(url_create, files=files, data=data)
    if resp.status_code != 200:
        print("Error generating create-token txn:", resp.text)
        return

    # 2) Deserialize, sign, and re-serialize the returned transaction
    txn_b64 = resp.json()  # base64-encoded VersionedTransaction
    txn_bytes = base64.b64decode(txn_b64)
    txn = VersionedTransaction.deserialize(txn_bytes)
    txn.sign([wallet])
    signed_b58 = base58.b58encode(txn.serialize()).decode()

    # 3) Send the signed txn via Jito RPC
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
