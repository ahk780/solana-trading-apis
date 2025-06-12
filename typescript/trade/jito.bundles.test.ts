import { Keypair, VersionedTransaction } from "@solana/web3.js";
import { bs58 } from "@project-serum/anchor/dist/cjs/utils/bytes";

const test = async () => {
  try {
    const wallets = [
      Keypair.fromSecretKey(bs58.decode("")),
      Keypair.fromSecretKey(bs58.decode("")),
      Keypair.fromSecretKey(bs58.decode("")),
      Keypair.fromSecretKey(bs58.decode("")),
    ];

    const param = [
      {
        wallet_address: wallets[0].publicKey.toBase58(),
        mint: "",
        action: "buy",
        dex: "jupiter",
        amount: 0.00001,
        tip: 0.002,
      },
      {
        wallet_address: wallets[1].publicKey.toBase58(),
        mint: "",
        action: "buy",
        dex: "jupiter",
        amount: 0.0001,
      },
      {
        wallet_address: wallets[2].publicKey.toBase58(),
        mint: "",
        action: "buy",
        dex: "jupiter",
        amount: 0.0001,
      },
      {
        wallet_address: wallets[3].publicKey.toBase58(),
        mint: "",
        action: "buy",
        dex: "jupiter",
        amount: 0.0001,
      },
    ];

    const url = "https://api.solanaportal.io/api/jito-bundle";
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
