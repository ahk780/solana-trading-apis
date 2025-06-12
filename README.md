# SolanaPortal Trading API

**Trade any token on Solana across multiple DEXes with unmatched speed, reliability, and the lowest fees.**


## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [API Endpoint](#api-endpoint)
- [Authentication](#authentication)
- [Request Parameters](#request-parameters)
- [Response](#response)
- [Usage Examples](#usage-examples)
  - [JavaScript (Node.js)](#javascript-nodejs)
  - [Python](#python)
- [Performance and Scalability](#performance-and-scalability)
- [Security](#security)
- [Contact & Support](#contact--support)
- [Contributing](#contributing)
- [License](#license)

## Introduction
SolanaPortal's Trading API lets you seamlessly execute buy and sell orders on major Solana-based DEXes and AMMs. Our service supports up to **500 RPS** with market-leading fees of **0.3%** and sub-`200ms` transaction creation latency on Pump.fun. Whether you're building a high-frequency trading bot or a DeFi application, SolanaPortal delivers the performance you need.

## Features
- **Multi-DEX Support**: Pump.fun AMM, Raydium, Meteora, Moonshot, Jupiter.
- **High Throughput**: Up to 500 requests per second on demand.
- **Low Fees**: Competitive fee of 0.3% per trade.
- **Ultra Low Latency**: ~200ms transaction creation time for Pump.fun.
- **Secure**: Your private keys never leave your machine.
- **Code Examples**: Pre-built examples in TypeScript and Python.
- **Active Development**: Continuous improvements and dedicated support.

## API Endpoint
```
POST https://api.solanaportal.io/api/trading
```

## Authentication
No API key is required. Signature-based authentication via your Solana private key is used to sign transactions locally.

## Request Parameters
| Parameter       | Type     | Description                                                       |
|-----------------|----------|-------------------------------------------------------------------|
| `wallet_address`| `string` | Your Solana wallet public address.                                |
| `action`        | `string` | `buy` or `sell`.                                                  |
| `dex`           | `string` | Target DEX (`pumpfun`, `raydium`, `meteora`, `moonshot`, `jupiter`). |
| `mint`          | `string` | Token mint address to trade.                                      |
| `amount`        | `number` | Amount in tokens or SOL.                                          |
| `slippage`      | `number` | Allowed slippage percentage (e.g., `0.5`).                        |
| `tip`           | `number` | Tip amount for Jito or bloXroute.                                 |
| `type`          | `string` | Relay option: `jito` or `bloxroute`.                              |

## Response
A JSON object containing an unsigned transaction:
```json
{
  "transaction": "<base64-encoded unsigned transaction>"
}
```
Sign and submit this transaction via your preferred RPC provider.

## Usage Examples

### JavaScript (Node.js)
```javascript
import fetch from 'node-fetch';
import {Keypair, Transaction} from '@solana/web3.js';

(async () => {
  const params = {
    wallet_address: 'YourPublicKey',
    action: 'buy',
    dex: 'pumpfun',
    mint: 'TokenMintAddress',
    amount: 1.0,
    slippage: 0.5,
    tip: 0.0001,
    type: 'jito'
  };

  const res = await fetch('https://api.solanaportal.io/api/trading', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(params),
  });
  const {transaction: txBase64} = await res.json();
  const tx = Transaction.from(Buffer.from(txBase64, 'base64'));
  // Sign and send using your connection...
})();
```

### Python
```python
import requests
from solana.transaction import Transaction
from solana.keypair import Keypair
import base64

params = {
    "wallet_address": "YourPublicKey",
    "action": "sell",
    "dex": "raydium",
    "mint": "TokenMintAddress",
    "amount": 2,
    "slippage": 0.5,
    "tip": 0.0001,
    "type": "bloxroute"
}

res = requests.post("https://api.solanaportal.io/api/trading", json=params)
tx = Transaction.deserialize(base64.b64decode(res.json()['transaction']))
# Sign and send...
```

## Performance and Scalability
SolanaPortal leverages private multi-region RPC endpoints to ensure consistent low-latency transaction creation. Our infrastructure scales horizontally to handle spikes of up to **500 RPS**.

## Security
- **Local Signing**: Transactions are created and signed locally; private keys never leave your environment.
- **Best Practices**: Always secure your private keys. Never share them or send them in plaintext.

## Contact & Support
- Telegram Support: [@ahk780](https://t.me/ahk780)
- Telegram Group: [Join our community](https://t.me/ahk782)
- GitHub Issues: Report bugs or request features via the [issue tracker](https://github.com/YourRepo/issues).

## Contributing
Contributions are welcome! Please fork the repository, make your changes, and open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
