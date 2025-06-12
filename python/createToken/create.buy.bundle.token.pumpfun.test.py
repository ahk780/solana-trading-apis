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

    # Decode secret and build 5 identical Keypairs
    secret = base58.b58decode(private_key_b58)
    wallets = [Keypair.from_secret_key(secret) for _ in range(5)]

    # 1) Upload metadata + image to IPFS (pump.fun)
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
    metadata     = ipfs_json["metadata"]
    metadata_uri = ipfs_json["metadataUri"]

    # 2) Build the bundle-creation payload
    create_url = "https://api.solanaportal.io/api/create/token/pumpfun"
    params = [
        {
            "name":         metadata["name"],
            "symbol":       metadata["symbol"],
            "metadataUri":  metadata_uri,
            "wallet_address": str(wallets[0].public_key),
            "amount":       0.00001,
            "slippage":     100,
            "tip":          0.0001,
            "type":         "jito",
        },
        {
            "wallet_address": str(wallets[1].public_key),
            "action":         "buy",
            "amount":         0.000001,
        },
        {
            "wallet_address": str(wallets[2].public_key),
            "action":         "buy",
            "amount":         0.000002,
        },
        {
            "wallet_address": str(wallets[3].public_key),
            "action":         "buy",
            "amount":         0.000003,
        },
        {
            "wallet_address": str(wallets[4].public_key),
            "action":         "buy",
            "amount":         0.000004,
        },
    ]
    create_resp = requests.post(create_url, json=params)
    if create_resp.status_code != 200:
        print("Error fetching bundle TXNs:", create_resp.text)
        return

    # 3) Deserialize, sign each TXN, and collect signatures
    unsigned_b64 = create_resp.json()  # list of base64-encoded TXNs
    signed_b58   = []
    signatures   = []
    for i, txn_b64 in enumerate(unsigned_b64):
        txn_bytes = base64.b64decode(txn_b64)
        txn       = VersionedTransaction.deserialize(txn_bytes)
        txn.sign([wallets[i]])
        # record first signature for logging
        sig = base58.b58encode(txn.signatures[0]).decode()
        signatures.append(sig)
        # serialize and base58-encode
        signed_bytes = txn.serialize()
        signed_b58.append(base58.b58encode(signed_bytes).decode())

    # 4) Send the signed bundle to Jito
    jito_url = "https://tokyo.mainnet.block-engine.jito.wtf/api/v1/bundles"
    payload = {
        "jsonrpc": "2.0",
        "id":      1,
        "method":  "sendBundle",
        "params":  [signed_b58],
    }
    jito_resp = requests.post(jito_url, json=payload)
    if jito_resp.status_code == 200:
        for idx, sig in enumerate(signatures):
            print(f"Transaction {idx}: https://solscan.io/tx/{sig}")
    else:
        print("Bundle failed:", jito_resp.text)

if __name__ == "__main__":
    main()
