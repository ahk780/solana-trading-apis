import { Keypair, VersionedTransaction } from "@solana/web3.js";
import { bs58 } from "@project-serum/anchor/dist/cjs/utils/bytes";
import { configDotenv } from "dotenv";
configDotenv();
//send jito bundles transactions for token buy/sell

const pk = process.env.PRIVATE_KEY;
const test = async () => {
  try {
    const private_key = pk || "";
    const wallet = Keypair.fromSecretKey(bs58.decode(private_key));
    console.log("wallet:", wallet.publicKey.toBase58());

    const param = {
      wallet_address: wallet.publicKey.toBase58(),
      mint: "",
    };

    const url = "https://api.solanaportal.io/api/create/market";
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
      const { market_id, serializedTxns } = data;
      console.log("market id:", market_id);
      const encodedSignedTxns = [];
      const signatures = [];
      for (let i = 0; i < serializedTxns.length; i++) {
        const txnBuffer = Buffer.from(serializedTxns[i], "base64");
        const txn = VersionedTransaction.deserialize(txnBuffer);
        txn.sign([wallet]);
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
            jitoResponse
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
