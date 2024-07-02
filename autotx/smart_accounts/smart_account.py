from abc import abstractmethod
from hexbytes import HexBytes
from web3 import Web3
from web3.types import TxReceipt

from autotx.intents import Intent
from autotx.transactions import TransactionBase
from autotx.eth_address import ETHAddress


class SmartAccount:
    web3: Web3
    address: ETHAddress

    def __init__(self, web3: Web3, address: ETHAddress):
        self.web3 = web3
        self.address = address

    def on_intents_prepared(self, intents: list[Intent]) -> None:
        pass

    @abstractmethod
    async def on_intents_ready(self, intents: list[Intent]) -> bool | str: # True if sent, False if declined, str if feedback
        raise NotImplementedError()

    @abstractmethod
    async def send_transaction(self, transaction: TransactionBase) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def send_transactions(self, transactions: list[TransactionBase]) -> None:
        raise NotImplementedError()

    def wait(self, tx_hash: HexBytes) -> TxReceipt:
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)