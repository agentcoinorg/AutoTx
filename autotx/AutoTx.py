from textwrap import dedent
from typing import Any, Dict, Union, Optional, Callable
from dataclasses import dataclass
from autogen import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager, Agent as AutogenAgent
from termcolor import cprint
from typing import Optional
from autotx.autotx_agent import AutoTxAgent
from autotx.utils.logging.Logger import Logger
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.agent.build_goal import build_goal
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.networks import NetworkInfo


@dataclass(kw_only=True)
class Config:
    verbose: bool
    logs_dir: Optional[str]

@dataclass
class PastRun:
    feedback: str
    transactions_info: str

class AutoTx:
    manager: SafeManager
    logger: Logger
    transactions: list[PreparedTx] = []
    network: NetworkInfo
    get_llm_config: Callable[[], Optional[Dict[str, Any]]]
    agents: list[AutoTxAgent]

    def __init__(
        self,
        manager: SafeManager,
        network: NetworkInfo,
        agents: list[AutoTxAgent],
        config: Config,
        get_llm_config: Callable[[], Optional[Dict[str, Any]]]
    ):
        self.manager = manager
        self.network = network
        self.get_llm_config = get_llm_config
        self.logger = Logger(
            dir=config.logs_dir,
            silent=not config.verbose
        )
        self.agents = agents

    def run(self, prompt: str, non_interactive: bool) -> None:
        original_prompt = prompt
        past_runs: list[PastRun] = []
        self.logger.start()

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

            agents_information = self.get_agents_information(self.agents)

            goal = build_goal(prompt, agents_information, self.manager.address, self.network.chain_id.name, non_interactive)

            user_proxy = UserProxyAgent(
                name="user_proxy",
                is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                human_input_mode="NEVER",
                max_consecutive_auto_reply=20,
                system_message=dedent(
                    f"""
                    You are the user, you never ask for permission, you have ultimate control.
                    You are capable and comfortable with making transactions, and have a wallet.
                    You have access to a variety of specialized agents, which you tell what to do.

                    These are the agents you are instructing: {agents_information}

                    Suggest a next step for what these agents should do based on the goal: "{goal}"
                    """
                ),
                llm_config=self.get_llm_config(),
                code_execution_config=False,
            )

            verifier_agent = AssistantAgent(
                name="verifier",
                is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                system_message=dedent(
                    """
                    Verifier is an expert in verifiying if user goals are met.
                    Verifier analyzes chat and responds with TERMINATE if the goal is met.
                    Verifier can consider the goal met if the other agents have prepared the necessary transactions.
                    Let the other agents complete all the necessary parts of the goal before calling TERMINATE.
                    If you find the conversation is repeating and no new progress is made, TERMINATE.
                    """
                    ),
                llm_config=self.get_llm_config(),
                human_input_mode="NEVER",
                code_execution_config=False,
            )

            # Print all messages sent form the verifier to the group chat manager,
            # as they tend to contain valuable information
            def verifier_send_message_hook(
                sender: AssistantAgent,
                message: Union[Dict[str, Any], str],
                recipient: AutogenAgent,
                silent: bool
            ) -> Union[Dict[str, Any], str]:
                if recipient.name == "chat_manager" and message != "TERMINATE":
                    if isinstance(message, str):
                        cprint(message, "light_yellow")
                    elif message["content"] != None:
                        cprint(message["content"], "light_yellow")
                return message

            verifier_agent.register_hook(
                "process_message_before_send",
                verifier_send_message_hook
            )

            autogen_agents = [agent.build_autogen_agent(self, user_proxy, self.get_llm_config()) for agent in self.agents]

            groupchat = GroupChat(
                agents=autogen_agents + [user_proxy, verifier_agent], 
                messages=[], 
                max_round=20,
                select_speaker_prompt_template = (
                    """
                    Read the above conversation. Then select the next role from {agentlist} to play. Only return the role and NOTHING else.
                    If agents are trying to communicate with the user, or requesting approval, return the 'user_proxy' role.
                    """
                )
            )
            manager = GroupChatManager(groupchat=groupchat, llm_config=self.get_llm_config())

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

        self.logger.stop()
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
