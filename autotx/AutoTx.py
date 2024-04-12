from textwrap import dedent
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from autogen import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager
from termcolor import cprint
from typing import Optional
from autogen.io import IOStream, IOConsole
from autotx.autotx_agent import AutoTxAgent
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.agent.build_goal import build_goal
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.io_silent import IOSilent


@dataclass(kw_only=True)
class Config:
    verbose: bool

@dataclass
class PastRun:
    feedback: str
    transactions_info: str

class AutoTx:
    manager: SafeManager
    config: Config = Config(verbose=False)
    transactions: list[PreparedTx] = []
    network: NetworkInfo
    get_llm_config: Callable[[], Optional[Dict[str, Any]]]
    agents: list[AutoTxAgent]

    def __init__(
        self, manager: SafeManager, network: NetworkInfo, agents: list[AutoTxAgent], config: Optional[Config],
        get_llm_config: Callable[[], Optional[Dict[str, Any]]]
    ):
        self.manager = manager
        self.network = network
        self.get_llm_config = get_llm_config
        if config:
            self.config = config
        self.agents = agents

    def run(self, prompt: str, non_interactive: bool, silent: bool = False) -> None:
        original_prompt = prompt
        past_runs: list[PastRun] = []

        while True:
            if past_runs:
                self.transactions.clear()
                
                prev_history = "".join(
                    [
                        dedent(f"""
                        Then you prepared these transactions to accomplish the goal:
                        {run.transactions_info}
                        Then the user provided feedback:
                        {run.feedback}
                        """)
                        for run in past_runs
                    ]
                )

                prompt = (f"\nOriginaly the user said: {original_prompt}"
                    + prev_history
                    + "Pay close attention to the user's feedback and try again.\n")

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

            agents_information = self.get_agents_information(self.agents)

            goal = build_goal(prompt, agents_information, self.manager.address, self.network.chain_id.name, non_interactive)

            verifier_agent = AssistantAgent(
                name="verifier",
                is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                system_message=dedent(
                        """
                        Verifier is an expert in verifiying if user goals are met.
                        Verifier analyzes chat and responds with TERMINATE if the goal is met.
                        Verifier can consider the goal met if the other agents have prepared the necessary transactions.
                    Let the other agents complete all the necessary parts of the goal before calling TERMINATE.
                        
                        If some information needs to be returned to the user or if there are any errors encountered during the process, add this in your answer.
                        Start any error messages with "ERROR:" to clearly indicate the issue. Then say the word TERMINATE.
                        Make sure to only add information if the user explicitly asks for a question that needs to be answered
                        or error details if user's request can not be completed.
                    """
                    ),
                llm_config=self.get_llm_config(),
                human_input_mode="NEVER",
                code_execution_config=False,
            )

            autogen_agents = [agent.build_autogen_agent(self, user_proxy, self.get_llm_config()) for agent in self.agents]

            groupchat = GroupChat(
                agents=autogen_agents + [user_proxy, verifier_agent], 
                messages=[], 
                max_round=20,
                select_speaker_prompt_template = (
                    """
                    Read the above conversation. Then select the next role from {agentlist} to play. Only return the role and NOTHING else.
                    """
                )
            )
            manager = GroupChatManager(groupchat=groupchat, llm_config=self.get_llm_config())

            if silent:
                IOStream.set_global_default(IOSilent())
            else:
                IOStream.set_global_default(IOConsole())

            chat = user_proxy.initiate_chat(manager, message=dedent(
                f"""
                    My goal is: {prompt}
                    Advisor reworded: {goal}
                """
            ))

            if "ERROR:" in chat.summary:
                error_message = chat.summary.replace("ERROR: ", "").replace("\n", "")
                cprint(error_message, "red")
            else:
                cprint(chat.summary.replace("\n", ""), "green")

            try:
                result = self.manager.send_tx_batch(self.transactions, require_approval=not non_interactive)

                if isinstance(result, str):
                    transactions_info ="\n".join(
                        [
                            f"{i + 1}. {tx.summary}"
                            for i, tx in enumerate(self.transactions)
                        ]
                    )
                                        
                    past_runs.append(PastRun(result, transactions_info))
                else:
                    break

            except Exception as e:
                cprint(e, "red")
                break

        self.transactions.clear()

    def get_agents_information(self, agents: list[AutoTxAgent]) -> str:
        agent_descriptions = []
        for agent in agents:
            tools_available = "\n".join(
                [
                    f"\n- {tool}"
                    for tool in agent.tool_descriptions
                ]
            )
            description = f"Agent name: {agent.name}\nTools available:{tools_available}"
            agent_descriptions.append(description)

        agents_information = "\n".join(agent_descriptions)

        return agents_information
