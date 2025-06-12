#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import base64
import base58
import requests
from solana.keypair import Keypair
from solana.transaction import VersionedTransaction

def main():
    # 1) Load your PRIVATE_KEY from .env
    load_dotenv()
    private_key_b58 = os.getenv("PRIVATE_KEY")
    if not private_key_b58:
        raise EnvironmentError("Missing PRIVATE_KEY in environment")

    # 2) Build your Solana wallet Keypair
    secret = base58.b58decode(private_key_b58)
    wallet = Keypair.from_secret_key(secret)
    print(f"wallet: {wallet.public_key}")

    # 3) Upload metadata + image to IPFS (pump.fun)
    ipfs_url = "https://pump.fun/api/ipfs"
    files = {"file": open("./zz.png", "rb")}
    data = {
        "name": "test",
        "symbol": "TEST",
        "description": "This is an example token created via SolanaPortal.AI",
        "twitter": "https://x.com/solana",
        "telegram": "https://x.com/solana",
        "website": "https://solanaportal.ai",
        "showName": "true",
    }

    ipfs_resp = requests.post(ipfs_url, files=files, data=data)
    if ipfs_resp.status_code != 200:
        print("Failed to create IPFS metadata storage:", ipfs_resp.text)
        return

    ipfs_json = ipfs_resp.json()
    # Expecting fields: metadata.name, metadata.symbol, metadataUri
    metadata       = ipfs_json["metadata"]
    metadata_uri   = ipfs_json["metadataUri"]

    # 4) Build the create-token/pumpfun payload
    create_url = "https://api.solanaportal.io/api/create/token/pumpfun"
    param = {
        "name":         metadata["name"],
        "symbol":       metadata["symbol"],
        "metadataUri":  metadata_uri,
        "wallet_address": str(wallet.public_key),
        "amount":       0.00001,
        # optional fields:
        # "slippage": 100,
        # "tip": 0.00005,
        # "type": "jito",
    }

    create_resp = requests.post(create_url, json=param)
    if create_resp.status_code != 200:
        print("Error generating create-token txn:", create_resp.text)
        return

    # 5) Deserialize, sign, and re-serialize the returned transaction
    txn_b64   = create_resp.json()
    txn_bytes = base64.b64decode(txn_b64)
    txn       = VersionedTransaction.deserialize(txn_bytes)
    txn.sign([wallet])
    signed_b58 = base58.b58encode(txn.serialize()).decode()

    # 6) Send the signed transaction via Jito RPC
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
