import { Keypair, VersionedTransaction } from "@solana/web3.js";
import { bs58 } from "@project-serum/anchor/dist/cjs/utils/bytes";
import { configDotenv } from "dotenv";
import fs from "fs";
configDotenv();

//Create pumpfun token and first buy

const pk = process.env.PRIVATE_KEY;
const test = async () => {
  try {
    const private_key = pk || "";
    const wallet = Keypair.fromSecretKey(bs58.decode(private_key));
    console.log("wallet:", wallet.publicKey.toBase58());

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

    const param = {
      name: metadataResponseJSON.metadata.name,
      symbol: metadataResponseJSON.metadata.symbol,
      metadataUri: metadataResponseJSON.metadataUri,
      wallet_address: wallet.publicKey.toBase58(), // Your wallet public key
      amount: 0.00001, // amount of SOL or tokens
      //optional
      // slippage: 100, // percent slippage allowed
      // tip: 0.00005, // priority fee
      // type: "jito", // "jito" or "bloxroute"
    };
    const url = "https://api.solanaportal.io/api/create/token/pumpfun";
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(param),
    });
    // return;
    if (response.status === 200) {
      // Successfully generated transaction
      const data = await response.json();
      const txnBuffer = Buffer.from(data, "base64");
      const txn = VersionedTransaction.deserialize(txnBuffer);
      txn.sign([wallet]);
      const signedTxnBuffer = bs58.encode(txn.serialize());
      const jitoResponse = await fetch(
        `https://tokyo.mainnet.block-engine.jito.wtf/api/v1/transactions`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            jsonrpc: "2.0",
            id: 1,
            method: "sendTransaction",
            params: [signedTxnBuffer],
          }),
        }
      );
      if (jitoResponse.status === 200) {
        const signature = (await jitoResponse.json()).result;
        console.log("- txn succeed", "https://solscan.io/tx/" + signature);
      } else {
        console.log("- txn failed, please check the parameters", data);
      }
    } else {
      console.log(response.statusText); // log error
    }
  } catch (e: any) {
    console.error(e.message);
  }
};

test();
