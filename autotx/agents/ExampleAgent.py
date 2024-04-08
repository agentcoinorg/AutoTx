from textwrap import dedent
from typing import Annotated, Callable
from autotx import AutoTx, AutoTxAgent, AutoTxTool

name = "Example Agent"

system_message = f"""
Example of an agent system message.
...
"""

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
    name=name
    system_message=dedent(system_message)
    tools=[
        ExampleTool(),
        # AnotherTool(...),
        # AndAnotherTool(...)
    ]
