#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import base64
import base58
import requests
from solana.keypair import Keypair
from solana.transaction import VersionedTransaction

def main():
    # Load keys from .env
    load_dotenv()
    priv_keys = [
        os.getenv("PRIVATE_KEY1", ""),
        os.getenv("PRIVATE_KEY2", ""),
        os.getenv("PRIVATE_KEY3", ""),
        os.getenv("PRIVATE_KEY4", ""),
    ]
    if not all(priv_keys):
        raise EnvironmentError(
            "Make sure PRIVATE_KEY1, PRIVATE_KEY2, PRIVATE_KEY3 and PRIVATE_KEY4 are set in your .env"
        )

    # Build Keypair objects
    wallets = [
        Keypair.from_secret_key(base58.b58decode(key_b58))
        for key_b58 in priv_keys
    ]

    # Construct the bundle request payload (matches your TS array)
    param = [
        {
            "wallet_address": str(wallets[0].public_key),
            "mint": "",
            "action": "buy",
            "dex": "jupiter",
            "amount": 0.00001,
            "tip": 0.002,
        },
        {
            "wallet_address": str(wallets[1].public_key),
            "mint": "",
            "action": "buy",
            "dex": "jupiter",
            "amount": 0.0001,
        },
        {
            "wallet_address": str(wallets[2].public_key),
            "mint": "",
            "action": "buy",
            "dex": "jupiter",
            "amount": 0.0001,
        },
        {
            "wallet_address": str(wallets[3].public_key),
            "mint": "",
            "action": "buy",
            "dex": "jupiter",
            "amount": 0.0001,
        },
    ]

    # 1) Ask SolanaPortal for the unsigned bundle
    bundle_url = "https://api.solanaportal.io/api/jito-bundle"
    resp = requests.post(bundle_url, json=param)
    if resp.status_code != 200:
        print("Error fetching bundle:", resp.text)
        return

    unsigned_txns_b64 = resp.json()  # should be a list of base64 strings

    # 2) Deserialize & sign each transaction
    signed_txns_b58 = []
    signatures = []
    for i, txn_b64 in enumerate(unsigned_txns_b64):
        txn_bytes = base64.b64decode(txn_b64)
        txn = VersionedTransaction.deserialize(txn_bytes)
        txn.sign([wallets[i]])
        # record the first signature for logging
        signatures.append(base58.b58encode(txn.signatures[0]).decode())
        # re-serialize the fully-signed txn
        signed_bytes = txn.serialize()
        signed_txns_b58.append(base58.b58encode(signed_bytes).decode())

    # 3) Send the signed bundle to Jito
    jito_url = "https://tokyo.mainnet.block-engine.jito.wtf/api/v1/bundles"
    jito_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendBundle",
        "params": [signed_txns_b58],
    }
    jito_resp = requests.post(jito_url, json=jito_payload)
    if jito_resp.status_code == 200:
        for idx, sig in enumerate(signatures):
            print(f"Transaction {idx}: https://solscan.io/tx/{sig}")
    else:
        print("Bundle failed:", jito_resp.text)

if __name__ == "__main__":
    main()
