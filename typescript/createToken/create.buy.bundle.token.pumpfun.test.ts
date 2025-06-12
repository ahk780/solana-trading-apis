import { Keypair, VersionedTransaction } from "@solana/web3.js";
import { bs58 } from "@project-serum/anchor/dist/cjs/utils/bytes";
import { configDotenv } from "dotenv";
import fs from "fs";
configDotenv();

//Create pumpfun tokena and buy bundles
//⚠️ Each buy amount should be different because jito can't send the same transaction as a bundle
const pk = process.env.PRIVATE_KEY;
const private_key = pk || "";
const test = async () => {
  try {
    const wallets = [
      Keypair.fromSecretKey(bs58.decode(private_key)),
      Keypair.fromSecretKey(bs58.decode(private_key)),
      Keypair.fromSecretKey(bs58.decode(private_key)),
      Keypair.fromSecretKey(bs58.decode(private_key)),
      Keypair.fromSecretKey(bs58.decode(private_key)),
    ];

    // Upload metadata to IPFS
    const image = await fs.openAsBlob("./zz.png");
    const formData = new FormData();
    formData.append("file", image); // Image file
    formData.append("name", "test");
    formData.append("symbol", "TEST");
    formData.append(
      "description",
      "This is an example token created via SolanaPortal.AI"
    );
    formData.append("twitter", "https://x.com/solana");
    formData.append("telegram", "https://x.com/solana");
    formData.append("website", "https://solanaportal.ai");
    formData.append("showName", "true");

    // Create IPFS metadata storage
    const metadataResponse = await fetch("https://pump.fun/api/ipfs", {
      method: "POST",
      body: formData,
    });
    if (metadataResponse.status !== 200) {
      throw new Error("Failed to create IPFS metadata storage");
    }
    const metadataResponseJSON = await metadataResponse.json();

    const param = [
      {
        name: metadataResponseJSON.metadata.name,
        symbol: metadataResponseJSON.metadata.symbol,
        metadataUri: metadataResponseJSON.metadataUri,
        wallet_address: wallets[0].publicKey.toBase58(), // Your wallet public key
        amount: 0.00001, // amount of SOL or tokens
        //optional
        slippage: 100, // percent slippage allowed
        tip: 0.0001, // priority fee
        type: "jito", // "jito" or "bloxroute"
      },
      {
        wallet_address: wallets[1].publicKey.toBase58(),
        action: "buy",
        amount: 0.000001, // ⚠! each buy amount should be different because jito can't send the same transaction as a bundle
      },
      {
        wallet_address: wallets[2].publicKey.toBase58(),
        action: "buy",
        amount: 0.000002, // ⚠! each buy amount should be different because jito can't send the same transaction as a bundle
      },
      {
        wallet_address: wallets[3].publicKey.toBase58(),
        action: "buy",
        amount: 0.000003, // ⚠! each buy amount should be different because jito can't send the same transaction as a bundle
      },
      {
        wallet_address: wallets[4].publicKey.toBase58(),
        action: "buy",
        amount: 0.000004, // ⚠! each buy amount should be different because jito can't send the same transaction as a bundle
      },
    ];

    const url = "https://api.solanaportal.io/api/create/token/pumpfun";
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(param),
    });
    if (response.status === 200) {
      // Successfully generated transaction
      const data = await response.json();

      const encodedSignedTxns = [];
      const signatures = [];
      for (let i = 0; i < data.length; i++) {
        const txnBuffer = Buffer.from(data[i], "base64");
        const txn = VersionedTransaction.deserialize(txnBuffer);
        txn.sign([wallets[i]]);
        signatures.push(bs58.encode(txn.signatures[0]));
        const signedTxnBuffer = txn.serialize();
        encodedSignedTxns.push(bs58.encode(signedTxnBuffer));
      }

      try {
        const jitoResponse = await fetch(
          `https://tokyo.mainnet.block-engine.jito.wtf/api/v1/bundles`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              jsonrpc: "2.0",
              id: 1,
              method: "sendBundle",
              params: [encodedSignedTxns],
            }),
          }
        );
        if (jitoResponse.status === 200) {
          for (let i = 0; i < signatures.length; i++) {
            console.log(
              `Transaction ${i}: https://solscan.io/tx/${signatures[i]}`
            );
          }
        } else {
          console.log(
            "bundle failed, please check the parameters",
            jitoResponse.statusText
          );
        }
      } catch (e: any) {
        console.error(e.message);
      }
    } else {
      console.log(response.statusText); // log error
    }
  } catch (e: any) {
    console.error(e.message);
  }
};

test();
