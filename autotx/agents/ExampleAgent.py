from textwrap import dedent
from autotx.AutoTx import AutoTx
from typing import Annotated, Callable
from autogen import AssistantAgent, UserProxyAgent, Agent
from autotx.autotx_agent import AutoTxAgent

example_info = {
    "name": "example_tool",
    "description": "Example of an agent tool."
}

def build_agent_factory() -> Callable[[AutoTx, UserProxyAgent, dict], Agent]:
    def agent_factory(autotx: AutoTx, user_proxy: UserProxyAgent, llm_config: dict) -> AutoTxAgent:
        agent = AssistantAgent(
            name="swap-tokens",
            system_message=dedent(f"""
                Example of an agent system message.
                """
            ),
            llm_config=llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
        )
    
        @user_proxy.register_for_execution()
        @agent.register_for_llm(
            name=example_info["name"],
            description=example_info["description"]
        )
        def example_tool(
            amount: Annotated[float, "Amount of something."],
            receiver: Annotated[str, "The receiver of something."]
        ) -> str:
            # TODO: do something useful
            print(f"ExampleTool run: {amount} {receiver}")
            
            # NOTE: you can add transactions to AutoTx's current bundle
            # self.autotx.transactions.append(tx)

            return f"Something useful has been done with {amount} to {receiver}"

        return AutoTxAgent(agent, tools=[
            f"{example_info['name']}: {example_info['description']}"
        ])

    return agent_factory
