from textwrap import dedent
from autotx.AutoTx import AutoTx
from typing import Annotated, Callable
from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool

class ExampleTool(AutoTxTool):
    name: str = "example_tool"
    description: str = dedent(
        """
        This tool does something very useful.
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable:
        def run(
            amount: Annotated[float, "Amount of something."],
            receiver: Annotated[str, "The receiver of something."]
        ) -> str:
            # TODO: do something useful
            print(f"ExampleTool run: {amount} {receiver}")
            
            # NOTE: you can add transactions to AutoTx's current bundle
            # autotx.transactions.append(tx)

            return f"Something useful has been done with {amount} to {receiver}"

        return run

class ExampleAgent(AutoTxAgent):
    name="swap-tokens"
    system_message=dedent(
        f"""
        Example of an agent system message.
        """
    )
    tools=[
        ExampleTool(),
        # AnotherTool(...),
        # AndAnotherTool(...)
    ]
