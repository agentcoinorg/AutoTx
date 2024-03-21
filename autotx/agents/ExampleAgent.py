from typing import Callable
from pydantic import ConfigDict, Field
from textwrap import dedent
from crewai import Agent
from crewai_tools import BaseTool
from autotx import AutoTx
from autotx.utils.llm import open_ai_llm
from autotx.utils.agents_config import AgentConfig, agents_config


class ExampleTool(BaseTool):
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
    model_config = ConfigDict(arbitrary_types_allowed=True)
    autotx: AutoTx = Field(None)

    def __init__(self, autotx: AutoTx):
        super().__init__()
        self.autotx = autotx

    def _run(
        self, amount: float, reciever: str
    ) -> str:

        # TODO: do something useful
        print(f"ExampleTool run: {amount} {reciever}")
        
        # NOTE: you can add transactions to AutoTx's current bundle
        # self.autotx.transactions.append(tx)

        return f"Something useful has been done with {amount} to {reciever}"


class ExampleAgent(Agent):
    name: str

    def __init__(self, autotx: AutoTx):
        name = "example-agent"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[
                ExampleTool(autotx),
                # AnotherTool(...),
                # AndAnotherTool(...)
            ],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name,
        )


def build_agent_factory() -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> ExampleAgent:
        return ExampleAgent(autotx)
    return agent_factory
