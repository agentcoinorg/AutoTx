import uuid

from web3 import Web3
from autotx import db, models
from autotx.utils.ethereum.SafeManager import SafeManager
from autotx.wallets.smart_wallet import SmartWallet


class ApiSmartWallet(SmartWallet):
    manager: SafeManager

    def __init__(self, web3: Web3, manager: SafeManager, tasks: db.TasksRepository, task_id: str | None = None):
        super().__init__(web3, manager.address)
        self.task_id = task_id
        self.manager = manager
        self.tasks = tasks

    def on_transactions_prepared(self, txs: list[models.Transaction]) -> None:
        if self.task_id is None:
            raise ValueError("Task ID is required")

        saved_task = self.tasks.get(self.task_id)
        if saved_task is None:
            raise ValueError("Task not found")

        for tx in txs:
            tx.id = str(uuid.uuid4())
            tx.task_id = self.task_id

        saved_task.transactions.extend(txs)
        self.tasks.update(saved_task)

    def on_transactions_ready(self, _txs: list[models.Transaction]) -> bool | str:
        return True