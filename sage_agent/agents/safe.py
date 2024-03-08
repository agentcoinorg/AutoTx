from eth_account import Account
from crewai import Agent
from pydantic import BaseModel, Field
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.ethereum.SafeManager import SafeManager
from sage_agent.utils.llm import open_ai_llm
from crewai_tools import BaseTool

class ExecuteTransactionsSchema(BaseModel):
    transactions: str = Field(..., description="A list of transactions to be executed")

class ExecuteTransactionsTool(BaseTool):
    name: str = "Execute a list of transactions in safe"
    description: str = "Executes a list of transactions in safe"
    safe: SafeManager | None = Field(None)
    agent: Account | None = Field(None)
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, safe: SafeManager, agent: Account):
        super().__init__()
        self.safe = safe
        self.agent = agent

    def _run(self, transactions: list[dict]) -> str:
        """
        :param transactions: list[dict], list of the transactions to be executed

        :return hash: str, hash of the executed multi-send transaction
        """
        for tx in transactions:
            tx["from"] = self.safe.address

        tx_hash = self.safe.send_txs(transactions)
        self.safe.wait(tx_hash)

        return tx_hash.hex()

# @tool("Creates and signs a transaction in safe")
# def create_transaction(payload: list[dict[str, Any]]) -> str:
#     """
#     Creates transaction in safe. It recieves an array of transactions, which will be
#     converted to a multisend transaction if necessary, if not, it just create a single transaction

#     Args:
#         payload: List of ethereum transactions
#     Returns:
#         str: Hash of the created safe transaction
#     """

#     # TODO: Be aware of user address if given
#     # manager = SafeManager.deploy_safe(
#     #     client, user, agent, [user.address, agent.address], 1
#     # )

#     (user, agent, client) = get_configuration()
#     manager = SafeManager(
#         client, user, agent, Safe("0x65D6359706D7a27e674a2C2D33b67cF6FB496Cd7", client)
#     )
#     manager.connect_multisend(contracts_config["safe"]["multisend_address"])
#     tx_hash = manager.send_txs([transaction_to_tx_params(tx) for tx in payload])
#     print("this is the tx hash! ", tx_hash)
#     # manager.wait(tx_hash)
#     return tx_hash

class SafeAgent(Agent):
    name: str

    def __init__(self, safe: SafeManager, agent: Account):
        name = "safe"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[
                ExecuteTransactionsTool(safe, agent),
            ],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name
        )
