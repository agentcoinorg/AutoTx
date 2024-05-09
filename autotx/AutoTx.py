from enum import Enum
from datetime import datetime
import json
import os
from textwrap import dedent
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from autogen import Agent as AutogenAgent
from termcolor import cprint
from typing import Optional
from autotx.autotx_agent import AutoTxAgent
from autotx.helper_agents import clarifier, manager, user_proxy
from autotx.utils.color import Color
from autotx.utils.logging.Logger import Logger
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.constants import OPENAI_BASE_URL, OPENAI_MODEL_NAME

@dataclass(kw_only=True)
class Config:
    verbose: bool
    logs_dir: Optional[str] = None
    log_costs: bool
    max_rounds: int

    def __init__(self, verbose: bool, logs_dir: Optional[str], max_rounds: Optional[int] = None, log_costs: Optional[bool] = None):
        self.verbose = verbose
        self.logs_dir = logs_dir
        self.log_costs = log_costs if log_costs is not None else False
        self.max_rounds = max_rounds if max_rounds is not None else 100

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
    total_cost_without_cache: float
    total_cost_with_cache: float
    info_messages: list[str]

class AutoTx:
    manager: SafeManager
    logger: Logger
    transactions: list[PreparedTx] = []
    network: NetworkInfo
    get_llm_config: Callable[[], Optional[Dict[str, Any]]]
    agents: list[AutoTxAgent]
    log_costs: bool
    max_rounds: int
    current_run_cost_without_cache: float = 0
    current_run_cost_with_cache: float = 0
    info_messages: list[str] = []
    verbose: bool

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
        self.log_costs = config.log_costs
        self.max_rounds = config.max_rounds
        self.verbose = config.verbose

    def run(self, prompt: str, non_interactive: bool, summary_method: str = "last_msg") -> RunResult:
        total_cost_without_cache: float = 0
        total_cost_with_cache: float = 0
        info_messages = []

        if self.verbose:
            print(f"LLM model: {OPENAI_MODEL_NAME}")
            print(f"LLM API URL: {OPENAI_BASE_URL}")

        while True:
            result = self.try_run(prompt, non_interactive, summary_method)
            total_cost_without_cache += result.total_cost_without_cache + self.current_run_cost_without_cache
            total_cost_with_cache += result.total_cost_with_cache + self.current_run_cost_with_cache
            info_messages += result.info_messages

            if result.end_reason == EndReason.TERMINATE or non_interactive:
                if self.log_costs:
                    now = datetime.now()
                    now_str = now.strftime('%Y-%m-%d-%H-%M-%S-') + str(now.microsecond)

                    if not os.path.exists("costs"):
                        os.makedirs("costs")
                    with open(f"costs/{now_str}.txt", "w") as f:
                        f.write(str(total_cost_without_cache))

                return RunResult(
                    result.summary, 
                    result.chat_history_json, 
                    result.transactions, 
                    result.end_reason, 
                    total_cost_without_cache, 
                    total_cost_with_cache, 
                    info_messages
                )
            else:
                prompt_not_supported = "Prompt not supported. Please provide a new prompt."

                cprint(prompt_not_supported, "yellow")
                info_messages.append(prompt_not_supported)

                prompt = input("Enter a new prompt: ")

    def try_run(self, prompt: str, non_interactive: bool, summary_method: str = "last_msg") -> RunResult:
        original_prompt = prompt
        past_runs: list[PastRun] = []
        self.current_run_costs_without_cache = 0
        self.current_run_costs_with_cache = 0
        self.info_messages = []
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

            self.notify_user("Running AutoTx with the following prompt: " + prompt)

            agents_information = self.get_agents_information(self.agents)

            user_proxy_agent = user_proxy.build(prompt, agents_information, self.get_llm_config)
            clarifier_agent = clarifier.build(user_proxy_agent, agents_information, not non_interactive, self.get_llm_config, self.notify_user)

            helper_agents: list[AutogenAgent] = [
                user_proxy_agent,
            ]

            if not non_interactive:
                helper_agents.append(clarifier_agent)

            autogen_agents = [agent.build_autogen_agent(self, user_proxy_agent, self.get_llm_config(), self.notify_user) for agent in self.agents]

            manager_agent = manager.build(autogen_agents + helper_agents, self.max_rounds, not non_interactive, self.get_llm_config)

            chat = user_proxy_agent.initiate_chat(
                manager_agent, 
                message=dedent(
                    f"""
                    I am currently connected with the following wallet: {self.manager.address}, on network: {self.network.chain_id.name}
                    My goal is: {prompt} 
                    """
                ), 
                summary_method=summary_method
            )

            if "ERROR:" in chat.summary:
                error_message = chat.summary.replace("ERROR: ", "").replace("\n", "")
                self.notify_user(error_message, "red")
            else:
                self.notify_user(chat.summary.replace("\n", ""), "green")

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
                self.notify_user(str(e), "red")
                break

        self.logger.stop()

        # Copy transactions to a new list to avoid modifying the original list
        transactions = self.transactions.copy()
        self.transactions.clear()

        chat_history = json.dumps(chat.chat_history, indent=4)

        return RunResult(chat.summary, chat_history, transactions, EndReason.TERMINATE if is_goal_supported else EndReason.GOAL_NOT_SUPPORTED, float(chat.cost["usage_including_cached_inference"]["total_cost"]), float(chat.cost["usage_excluding_cached_inference"]["total_cost"]), self.info_messages)

    def notify_user(self, message: str, color: Color | None = None) -> None:
        if color:
            cprint(message, color)
        else:
            print(message)
        self.info_messages.append(message)

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
