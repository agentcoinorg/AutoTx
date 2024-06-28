import asyncio
import json
from typing import cast
import aiohttp
from eth_account.signers.local import LocalAccount
from web3 import Web3

from autotx.eth_address import ETHAddress
from autotx.intents import Intent
from autotx.transactions import TransactionBase
from autotx.smart_accounts.smart_account import SmartAccount
from autotx.utils.ethereum.networks import NetworkInfo

class LocalBiconomySmartAccount(SmartAccount):
    web3: Web3
    owner: LocalAccount
    auto_submit_tx: bool

    def __init__(self, web3: Web3, owner: LocalAccount, auto_submit_tx: bool):
        self.web3 = web3
        self.owner = owner
        self.auto_submit_tx = auto_submit_tx
        address = asyncio.run(self.get_address())
        super().__init__(web3, ETHAddress(address))

    def on_intents_prepared(self, intents: list[Intent]) -> None:
        pass

    async def on_intents_ready(self, intents: list[Intent]) -> bool | str:
        if self.auto_submit_tx: 
            if not intents:
                return False

            transactions: list[TransactionBase] = []

            for intent in intents:
                transactions.extend(await intent.build_transactions(self.web3, NetworkInfo(self.web3.eth.chain_id), self.address))

            dict_transactions = [json.loads(transaction.json()) for transaction in transactions]

            await self.send_transactions(dict_transactions)

            return True
        else:
            return False

    async def get_address(self) -> str:
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"http://localhost:7080/api/v1/account/address?chainId={self.web3.eth.chain_id}",
                headers={"Content-Type": "application/json"},
            )

            if response.status != 200:
                raise ValueError(f"Failed to get address: Biconomy API internal error")
            
            return cast(str, await response.json())

    async def send_transaction(self, transaction: TransactionBase) -> None:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"http://localhost:7080/api/v1/account/transactions?chainId={self.web3.eth.chain_id}",
                headers={"Content-Type": "application/json"},
                data=json.dumps([transaction]),
            )
            if response.status != 200:
                raise ValueError(f"Transaction failed: {await response.json()}")

            print(f"Transaction sent: {await response.json()}")

    async def send_transactions(self, transactions: list[TransactionBase]) -> None:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"http://localhost:7080/api/v1/account/transactions?chainId={self.web3.eth.chain_id}",
                headers={"Content-Type": "application/json"},
                data=json.dumps(transactions)
            )
            if response.status != 200:
                raise ValueError(f"Transaction failed: Biconomy API internal error")

            print(f"Transaction sent: {await response.json()}")