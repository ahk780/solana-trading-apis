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
    formData.append("image", image); // Image file
    formData.append("wallet_address", wallet.publicKey.toBase58()); // Image file
    formData.append("name", "test");
    formData.append("symbol", "TEST");
    formData.append("decimals", "6");
    formData.append("total_supply", "1000000");
    formData.append("sellerFeeBasisPoints", "0");
    formData.append(
      "description",
      "This is an example token created via SolanaPortal.AI"
    );
    formData.append("twitter", "https://x.com/solana");
    formData.append("telegram", "https://x.com/solana");
    formData.append("website", "https://solanaportal.ai");

    const url = "https://api.solanaportal.io/api/create/token/normal";
    const response = await fetch(url, {
      method: "POST",
      body: formData,
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
