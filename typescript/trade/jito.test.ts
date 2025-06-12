import { bs58 } from "@project-serum/anchor/dist/cjs/utils/bytes";
import { Keypair, VersionedTransaction } from "@solana/web3.js";
import { configDotenv } from "dotenv";
configDotenv();

//Send jito transaction for token buy/sell

const pk = process.env.PRIVATE_KEY;
const test = async () => {
  try {
    const private_key = pk || "";
    const wallet = Keypair.fromSecretKey(bs58.decode(private_key));
    console.log("wallet:", wallet.publicKey.toBase58());
    const mint = "";
    const param = {
      wallet_address: wallet.publicKey.toBase58(), // Your wallet public key
      action: "sell", // "buy" or "sell"
      dex: "pumpfun", // dex name
      mint, // contract address of the token you want to trade
      amount: 355486.039918, // amount of SOL or tokens
      slippage: 20, // percent slippage allowed
      tip: 0.0005, // priority fee
      type: "jito", // "jito" or "bloxroute"
    };

    const url = "https://api.solanaportal.io/api/trading";
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(param),
    });
    // return;
    if (response.status === 200) {
      // successfully generated transaction
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
