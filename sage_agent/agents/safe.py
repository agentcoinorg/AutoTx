from langchain_core.tools import tool
from crewai import Agent
from pydantic import BaseModel, Field
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.ethereum import SafeManager
from sage_agent.utils.llm import open_ai_llm
from web3.types import TxParams
from gnosis.safe import Safe
from sage_agent.utils.user import get_configuration


class Transaction(BaseModel):
    to: str = Field(description="Target address of transaction")
    data: str = Field(description="Calldata of transaction to be executed")
    # from_address: str = Field(
    #     ..., alias="from", description="Address that is sending the transaction"
    # )
    value: str = Field(description="Value of ether sent in transaction")


def convert_tx_params_to_transaction(tx_params: TxParams) -> Transaction:
    return Transaction(
        to=str(tx_params.get("to", "")),
        data=str(tx_params.get("data", "")),
        # from_address=str(
        #     tx_params.get("from", "")
        # ),  # '_from' is the adjusted field name for 'from'
        value=str(
            tx_params.get("value", "0")
        )
    )


@tool("Creates and signs a transaction in safe")
def create_transaction(payload: list[TxParams]) -> str:
    """
    Creates transaction in safe. It recieves an array of transactions, which will be
    converted to a multisend transaction if necessary, if not, it just create a single transaction

    Args:
        payload: List of ethereum transactions
    Returns:
        str: Hash of the created safe transaction
    """

    # TODO: Be aware of user address if given
    (user, agent, client) = get_configuration()
    # manager = SafeManager.deploy_safe(
    #     client, user, agent, [user.address, agent.address], 1
    # )

    manager = SafeManager(
        client, user, agent, Safe("0x65D6359706D7a27e674a2C2D33b67cF6FB496Cd7", client)
    )
    tx_hash = manager.send_txs(payload)
    print("this is the tx hash! ", tx_hash)
    # manager.wait(tx_hash)
    return tx_hash


default_tools = [
    create_transaction,
    # execute_transaction,
    # sign_transaction,
]


class SafeAgent(Agent):
    name: str

    def __init__(self):
        name = "safe"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=default_tools,
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name
        )
