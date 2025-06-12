import { Keypair, VersionedTransaction } from "@solana/web3.js";
import { bs58 } from "@project-serum/anchor/dist/cjs/utils/bytes";
import { configDotenv } from "dotenv";
configDotenv();

//Create trading transaction using bloxroute

const pk = process.env.PRIVATE_KEY;
const test = async () => {
  try {
    const private_key = pk || "";
    const wallet = Keypair.fromSecretKey(bs58.decode(private_key));
    const mint = "";
    const param = {
      wallet_address: wallet.publicKey.toBase58(), // Your wallet public key
      action: "buy", // "buy" or "sell"
      mint, // contract address of the token you want to trade
      dex: "jupiter", // exchange to trade on. "pumpfun" or "raydium"
      amount: 0.00001, // amount of SOL or tokens
      slippage: 100, // percent slippage allowed
      tip: 0.001, // priority fee
      type: "bloxroute", // "jito" or "bloxroute"
    };

    const url = "https://api.solanaportal.io/api/trading";
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(param),
    });
    if (response.status === 200) {
      // successfully generated transaction
      const data = await response.json();
      const txnBuffer = Buffer.from(data, "base64");
      const txn = VersionedTransaction.deserialize(txnBuffer);

      txn.sign([wallet]);

      const param = {
        encodedTxn: Buffer.from(txn.serialize()).toString("base64"),
      };
      const url = "https://api.solanaportal.io/api/bloxroute";
      const bloxrouteRes = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(param),
      });
      if (bloxrouteRes.status === 200) {
        const signature = (await bloxrouteRes.json()).signature;
        console.log("- txn succeed", "https://solscan.io/tx/" + signature);
      } else {
        console.log("- txn failed, please check the parameters");
      }
    } else {
      console.log(response.statusText); // log error
    }
  } catch (e: any) {
    console.error(e.message);
  }
};

test();
