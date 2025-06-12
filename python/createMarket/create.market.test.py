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

    # 1) Create market (prepare bundle of TXNs)
    create_url = "https://api.solanaportal.io/api/create/market"
    param = {
        "wallet_address": str(wallet.public_key),
        "mint": ""  # fill in your mint address
    }
    resp = requests.post(create_url, json=param)
    if resp.status_code != 200:
        print("Error creating market bundle:", resp.text)
        return

    data = resp.json()
    market_id = data.get("market_id")
    serialized_txns = data.get("serializedTxns", [])
    print(f"market id: {market_id}")

    # 2) Deserialize & sign each TXN, collect signatures and signed TXNs
    encoded_signed_txns = []
    signatures = []
    for tx_b64 in serialized_txns:
        txn_bytes = base64.b64decode(tx_b64)
        txn = VersionedTransaction.deserialize(txn_bytes)
        txn.sign([wallet])
        sig = base58.b58encode(txn.signatures[0]).decode()
        signatures.append(sig)
        signed_bytes = txn.serialize()
        encoded_signed_txns.append(base58.b58encode(signed_bytes).decode())

    # 3) Send the signed bundle via Jito
    jito_url = "https://tokyo.mainnet.block-engine.jito.wtf/api/v1/bundles"
    jito_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendBundle",
        "params": [encoded_signed_txns],
    }
    jito_resp = requests.post(jito_url, json=jito_payload)
    if jito_resp.status_code == 200:
        for i, sig in enumerate(signatures):
            print(f"Transaction {i}: https://solscan.io/tx/{sig}")
    else:
        print("Bundle failed:", jito_resp.text)

if __name__ == "__main__":
    main()
