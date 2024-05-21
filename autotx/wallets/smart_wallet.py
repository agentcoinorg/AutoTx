from abc import abstractmethod
from autotx import models
from autotx.utils.ethereum.eth_address import ETHAddress


class SmartWallet:
    def __init__(self, address: ETHAddress):
        self.address = address

    def on_transactions_prepared(self, txs: list[models.Transaction]) -> None:
        pass

    @abstractmethod
    def on_transactions_ready(self, txs: list[models.Transaction]) -> bool | str: # True if sent, False if declined, str if feedback
        pass
