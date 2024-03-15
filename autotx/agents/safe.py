import json
from eth_account import Account
from crewai import Agent
from pydantic import ConfigDict, Field
from autotx.utils.agents_config import AgentConfig, agents_config
from autotx.utils.ethereum.SafeManager import SafeManager
from autotx.utils.llm import open_ai_llm
from crewai_tools import BaseTool
from web3.types import TxParams
import ast


class ExecuteTransactionsTool(BaseTool):
    name: str = "Execute a list of transactions in safe"
    description: str = "Executes a list of transactions in safe"

    model_config = ConfigDict(arbitrary_types_allowed=True)
    safe: SafeManager | None = Field(None)
    agent: Account | None = Field(None)

    def __init__(self, safe: SafeManager, agent: Account):
        super().__init__()
        self.safe = safe
        self.agent = agent

    def _run(self, transactions: str) -> str:
        """
        :param transactions: str, strigified list of transactions to be executed

        example of transactions list: [{
          "to": str,
          "data": str,
          "value": str,
          "gas": int,
          "maxFeePerGas": int,
          "chainId": int,
          "maxPriorityFeePerGas": int
        }]

        :return hash: str, hash of the executed multi-send transaction
        """
        sanitized_transaction: list[TxParams] = self.sanitize_transactions(transactions)

        tx_hash = self.safe.send_multisend_tx(sanitized_transaction)
        self.safe.wait(tx_hash)

        return tx_hash.hex()

    def sanitize_transactions(self, transactions: str):
        try:
            return ast.literal_eval(transactions)
        except Exception:
            return json.loads(transactions)


class SafeAgent(Agent):
    name: str

    def __init__(self, safe: SafeManager, agent: Account):
        name = "safe"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[ExecuteTransactionsTool(safe, agent)],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name,
        )
