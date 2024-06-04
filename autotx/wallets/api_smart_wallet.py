import uuid

from web3 import Web3
from autotx import models
from autotx.utils.ethereum.SafeManager import SafeManager
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.wallets.smart_wallet import SmartWallet


class ApiSmartWallet(SmartWallet):
    manager: SafeManager

    def __init__(self, web3: Web3, manager: SafeManager, task_id: str, tasks: list[models.Task]):
        super().__init__(web3, manager.address)
        self.task_id = task_id
        self.tasks = tasks
        self.manager = manager

    def on_transactions_prepared(self, txs: list[models.Transaction]) -> None:
        saved_task = next(filter(lambda x: x.id == self.task_id, self.tasks), None)
        if saved_task is None:
            raise Exception("Task not found: " + self.task_id)
        for tx in txs:
            tx.id = str(uuid.uuid4())
            tx.task_id = self.task_id

        saved_task.transactions.extend(txs)

    def on_transactions_ready(self, _txs: list[models.Transaction]) -> bool | str:
        return True