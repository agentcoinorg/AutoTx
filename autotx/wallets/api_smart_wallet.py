from web3 import Web3
from autotx import db
from autotx.intents import Intent
from autotx.transactions import Transaction
from autotx.utils.ethereum.SafeManager import SafeManager
from autotx.wallets.smart_wallet import SmartWallet


class ApiSmartWallet(SmartWallet):
    manager: SafeManager

    def __init__(self, web3: Web3, manager: SafeManager, tasks: db.TasksRepository, task_id: str | None = None):
        super().__init__(web3, manager.address)
        self.task_id = task_id
        self.manager = manager
        self.tasks = tasks

    def on_intents_prepared(self, intents: list[Intent]) -> None:
        if self.task_id is None:
            raise ValueError("Task ID is required")

        saved_task = self.tasks.get(self.task_id)
        if saved_task is None:
            raise ValueError("Task not found")

        saved_task.intents.extend(intents)
        self.tasks.update(saved_task)

    async def on_intents_ready(self, _intents: list[Intent]) -> bool | str:
        return True