# AutoTx
[Discord](https://discord.gg/k7UCsH3ps9) | :star: the repo !  

![](./docs/img/banner.png)


AutoTx is a personal assistant that plans and proposes on-chain transactions for you. These tx bundles are submitted to a smart account so users can easily execute them.

> [!WARNING]  
> This project is still early and experimental. Exercise caution when using real funds.  

## How It Works

AutoTx employs a multi-agent orchestration architecture to easily compose functionality. Given a user's prompt, it will first create a plan for how it will satisfy the user's intents. During the plan's execution, individual agents are used to complete tasks described within the plan.

Agents can add transactions to the bundle, which will later be proposed to the user's smart account for final approval before on-chain execution. Currently AutoTx supports [Safe](https://safe.global/) smart accounts. AutoTx uses a locally-stored private key to submit transaction to the user's smart account. AutoTx can create a new smart account for the user, or connect to an existing account (instructions below).

## Agents

Below is a list of existing and anticipated agents that AutoTx can use. If you'd like to help build one of these agents, see the [How To Contribute](#how-to-contribute) section below.

| Agent | Description | Status |
|-|-|-|
| [Send Tokens](./autotx/agents/SendTokensAgent.py) | Send tokens (ERC20 & ETH) to a receiving address. | :rocket: |
| [Swap Tokens](./autotx/agents/SwapTokensAgent.py) | Swap from one token to another. Currently integrated with Uniswap. | :rocket: |
| Bridge Tokens | Bridge tokens from one chain to another. | :memo: [draft](https://github.com/polywrap/AutoTx/issues/46) |
| NFTs | Basic NFT integration: mint, transfer, set approval, etc. | :memo: [draft](https://github.com/polywrap/AutoTx/issues/45) |
| NFT Market | NFT marketplace functionality: list, bid, etc. | :thought_balloon: |
| Token Search | Research tokens, liquidity, prices, graphs, etc. | :thought_balloon: |
| Earn Yield | Stake assets to earn yield. | :thought_balloon: |
| LP | Provide liquidity to AMMs. | :thought_balloon: |
| Governance | Vote or delegate in DAOs. | :thought_balloon: |
| Predict | Generate future predictions based on research. | :thought_balloon: |
| Donate | Donate to public goods projects. | :thought_balloon: |
| Invest | Participate in LBPs, IDOs, etc. | :thought_balloon: |
| Social | Use social networks (ex: Farcaster). | :thought_balloon: |

# Getting Started
## Pre-Requisites
Please install the following:
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [python](https://www.python.org/downloads/)
- [poetry](https://python-poetry.org/docs/#installation)
- [docker](https://www.docker.com/)

## Installation
1. Clone the repository via `git clone https://github.com/polywrap/AutoTx` and `cd AutoTx` into the directory.
2. Create a new .env file via `cp .env.template .env`
3. Find the line that says OPENAI_API_KEY=, and add your unique OpenAI API Key `OPENAI_API_KEY=sk-...`
4. Find the line that says CHAIN_RPC_URL=, and add your unique Ethereum RPC URL `CHAIN_RPC_URL=https://mainnet.infura.io/v3/...` (see https://www.infura.io/)
5. Start a new poetry shell `poetry shell`
6. Install python dependencies `poetry install`

## Run The Agent

1. AutoTx requires a fork of the blockchain network you want to transaction against. You can start the fork by running `poetry run start-fork`, and stop it with `poetry run stop-fork`. This command requires Docker to be running on your computer.
2. Run `poetry run ask` and provide a prompt for AutoTx to work on solving for you (ex: `Send 1 ETH to vitalik.eth`). The `--prompt "..."` option can be used for non-interactive startup.

> [!NOTE]  
> All transactions will happen offline with test network funds. Instructions on how to connect AutoTx with an existing smart account will be added shortly.  

## Prompts
AutoTx currently supports prompts such as:
* `Send 1 ETH to vitalik.eth`  
* `Buy 100 USDC with ETH`  
* `Swap ETH to 0.05 WBTC, then swap WBTC to 1000 USDC, and finally send 50 USDC to 0x...`  

Future possibilities:
* `Send the most popular meme coin to vitalik.eth`
* `Purchase mainnet ETH with my USDC on optimism`
* `What proposals are being voted on right now?`
* `Donate $100 to environmental impact projects.`

## How To Contribute
Interested in contributing to AutoTx? There's no shortage of [agents](#agents) to build, as well as we keep the [repository's issues](https://github.com/polywrap/AutoTx/issues) updated. Connecting with us on [Discord](https://discord.gg/k7UCsH3ps9) if you have any questions or ideas to share.

### Adding Agents

To add agents to AutoTx, we recommend starting with the [`ExampleAgent.py`](./autotx/agents/ExampleAgent.py) starter template. From there you'll want to:
1. Implement the tools (functions) you want the agent to be able to call.
2. Add all tools to the agent's `tools=[...]` array.
3. Add your new agent to `AutoTx`'s constructor in [`cli.py`](./autotx/cli.py).

### Testing Agents

Tests are located in the [`./autotx/tests`](./autotx/tests/) directory.

Use the following commands to run your tests:
```bash
# run all tests
poetry run pytest -s

# run a specific file
poetry run pytest -s ./autotx/tests/file_name.py

# run a specific test
poetry run pytest -s ./autotx/tests/file_name.py::function_name
```

## Need Help?

Join our [Discord community](https://discord.gg/k7UCsH3ps9) for support and discussions.

[![Join us on Discord](https://invidget.switchblade.xyz/k7UCsH3ps9)](https://discord.com/invite/k7UCsH3ps9)

If you have questions or encounter issues, please don't hesitate to [create a new issue](https://github.com/polywrap/AutoTx/issues/new) to get support.
