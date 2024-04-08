from textwrap import dedent
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from autogen import UserProxyAgent, AssistantAgent, Agent, GroupChat, GroupChatManager
from typing import Optional
from autotx.autotx_agent import AutoTxAgent
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.agent.build_goal import build_goal
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.networks import NetworkInfo

@dataclass(kw_only=True)
class Config:
    verbose: bool

class AutoTx:
    manager: SafeManager
    config: Config = Config(verbose=False)
    transactions: list[PreparedTx] = []
    network: NetworkInfo
    get_llm_config: Callable[[], Optional[Dict[str, Any]]]
    user_proxy: UserProxyAgent
    agent_factories: list[Callable[['AutoTx', UserProxyAgent, Optional[Dict[str, Any]]], AutoTxAgent]]

    def __init__(
        self, manager: SafeManager, network: NetworkInfo, agent_factories: list[Callable[['AutoTx', UserProxyAgent, Optional[Dict[str, Any]]], Agent]], config: Optional[Config],
        get_llm_config: Callable[[], Optional[Dict[str, Any]]]
    ):
        self.manager = manager
        self.network = network
        self.get_llm_config = get_llm_config
        if config:
            self.config = config
        self.agent_factories = agent_factories

    def run(self, prompt: str, non_interactive: bool):
        print("Running AutoTx with the following prompt: ", prompt)

        user_proxy = UserProxyAgent(
            name="user_proxy",
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=20,
            system_message=f"You are a user proxy. You will be interacting with the agents to accomplish the tasks.",
            llm_config=self.get_llm_config(),
            code_execution_config=False,
        )
        agents = [factory(self, user_proxy, self.get_llm_config()) for factory in self.agent_factories]

        agents_information = self.get_agents_information(agents)

        goal = build_goal(prompt, agents_information, self.manager.address, non_interactive)

        verifier_agent = AssistantAgent(
            name="verifier",
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            system_message=dedent(
                    """
                    You are an expert in verifiying if user goals are met.
                    You analyze chat and respond with TERMINATE if the goal is met.
                    You can consider the goal met if the other agents have prepared the necessary transactions.
                    """
                ),
            llm_config=self.get_llm_config(),
            human_input_mode="NEVER",
            code_execution_config=False,
        )

        groupchat = GroupChat(agents=[agent.autogen_agent for agent in agents] + [user_proxy, verifier_agent], messages=[], max_round=12)
        manager = GroupChatManager(groupchat=groupchat, llm_config=self.get_llm_config())

        user_proxy.initiate_chat(manager, message=dedent(
            f"""
                My goal is: {prompt}
                Advisor reworded: {goal}
            """
        ))

        self.manager.send_tx_batch(self.transactions, require_approval=not non_interactive)
        self.transactions.clear()
       

    def get_agents_information(self, agents: list[AutoTxAgent]) -> str:
        agent_descriptions = []
        for agent in agents:
            tools_available = "\n".join(
                [
                    f"\n- {tool}"
                    for tool in agent.tools
                ]
            )
            description = f"Agent name: {agent.autogen_agent.name}\nTools available:{tools_available}"
            agent_descriptions.append(description)

        agents_information = "\n".join(agent_descriptions)

        return agents_information
