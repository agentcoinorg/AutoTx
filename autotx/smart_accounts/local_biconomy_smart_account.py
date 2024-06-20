import json
import requests
from eth_account.signers.local import LocalAccount
from web3 import Web3

from autotx.intents import Intent
from autotx.transactions import TransactionBase
from autotx.smart_accounts.smart_account import SmartAccount

class LocalBiconomySmartAccount(SmartAccount):
    web3: Web3
    owner: LocalAccount
    auto_submit_tx: bool

    def __init__(self, web3: Web3, owner: LocalAccount, auto_submit_tx: bool):
        super().__init__(web3, owner.address)

        self.web3 = web3
        self.owner = owner
        self.auto_submit_tx = auto_submit_tx

    def on_intents_prepared(self, intents: list[Intent]) -> None:
        pass

    async def on_intents_ready(self, intents: list[Intent]) -> bool | str:
        return False

    def send_transaction(self, transaction: TransactionBase) -> None:
        response = requests.post(
            f"http://localhost:3000/api/v1/account/transactions?account={self.owner.address}&chainId={self.web3.eth.chain_id}",
            json=json.dumps([transaction]),
        )

        if response.status_code != 200:
            raise ValueError(f"Transaction failed: {response.json()}")

    def send_transactions(self, transactions: list[TransactionBase]) -> None:
        response = requests.post(
            f"http://localhost:3000/api/v1/account/transactions?account={self.owner.address}&chainId={self.web3.eth.chain_id}",
            json=json.dumps(transactions),
        )

        if response.status_code != 200:
            raise ValueError(f"Transaction failed: {response.json()}")
