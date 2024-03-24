from typing import Callable
from textwrap import dedent
from crewai import Agent
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from autotx.auto_tx_tool import AutoTxTool

class ExampleTool(AutoTxTool):
    name: str = "Example tool that does something useful"
    description: str = dedent(
        """
        This tool does something very useful.

        Args:
            amount (float): Amount of something.
            reciever (str): The reciever of something.
        Returns:
            The result of the useful tool in a useful format.
        """
    )

    def _run(
        self, amount: float, reciever: str
    ) -> str:

        # TODO: do something useful
        print(f"ExampleTool run: {amount} {reciever}")
        
        # NOTE: you can add transactions to AutoTx's current bundle
        # self.autotx.transactions.append(tx)

        return f"Something useful has been done with {amount} to {reciever}"

class ExampleAgent(AutoTxAgent):
    def __init__(self, autotx: AutoTx):
        super().__init__(
            name="example-agent",
            role="Example agent role",
            goal="Example agent goal",
            backstory="Example agent backstory",
            tools=[
                ExampleTool(autotx),
                # AnotherTool(...),
                # AndAnotherTool(...)
            ],
        )

def build_agent_factory() -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> ExampleAgent:
        return ExampleAgent(autotx)
    return agent_factory
