from enum import Enum
import json
from textwrap import dedent
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from autogen import Agent as AutogenAgent
from termcolor import cprint
from typing import Optional
from autotx.autotx_agent import AutoTxAgent
from autotx.helper_agents import clarifier, manager, user_proxy, verifier
from autotx.utils.logging.Logger import Logger
from autotx.utils.PreparedTx import PreparedTx
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

class EndReason(Enum):
    TERMINATE = "TERMINATE"
    GOAL_NOT_SUPPORTED = "GOAL_NOT_SUPPORTED"

@dataclass
class RunResult:
    summary: str
    chat_history_json: str
    transactions: list[PreparedTx]
    end_reason: EndReason

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

    def run(self, prompt: str, non_interactive: bool, summary_method: str = "last_msg") -> RunResult:
        while True:
            result = self.try_run(prompt, non_interactive, summary_method)
            if result.end_reason == EndReason.TERMINATE or non_interactive:
                return result
            else:
                cprint("Prompt not supported. Please provide a new prompt.", "yellow")
                prompt = input("Enter a new prompt: ")

    def try_run(self, prompt: str, non_interactive: bool, summary_method: str = "last_msg") -> RunResult:
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

            user_proxy_agent = user_proxy.build(prompt, agents_information, self.get_llm_config)
            clarifier_agent = clarifier.build(user_proxy_agent, agents_information, self.manager.address, self.network.chain_id.name, non_interactive, self.get_llm_config)

            helper_agents: list[AutogenAgent] = [
                user_proxy_agent,
                verifier.build(self.get_llm_config),
                clarifier_agent
            ]

            autogen_agents = [agent.build_autogen_agent(self, user_proxy_agent, self.get_llm_config()) for agent in self.agents]

            manager_agent = manager.build(autogen_agents + helper_agents, self.get_llm_config)

            chat = user_proxy_agent.initiate_chat(manager_agent, message=prompt, summary_method=summary_method)

            if "ERROR:" in chat.summary:
                error_message = chat.summary.replace("ERROR: ", "").replace("\n", "")
                cprint(error_message, "red")
            else:
                cprint(chat.summary.replace("\n", ""), "green")

            is_goal_supported = chat.chat_history[-1]["content"] != "Goal not supported: TERMINATE"

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

        # Copy transactions to a new list to avoid modifying the original list
        transactions = self.transactions.copy()
        self.transactions.clear()

        chat_history = json.dumps(chat.chat_history, indent=4)

        return RunResult(chat.summary, chat_history, transactions, EndReason.TERMINATE if is_goal_supported else EndReason.GOAL_NOT_SUPPORTED)

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
