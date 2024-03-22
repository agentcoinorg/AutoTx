import json
from typing import Optional, Callable
from dataclasses import dataclass
from textwrap import dedent
import openai
from typing import Optional
import typing
from crewai import Agent, Crew, Process, Task
from autotx.utils.agent.build_goal import build_goal
from autotx.utils.agent.define_tasks import define_tasks
from autotx.utils.agents_config import agents_config
from langchain_core.tools import StructuredTool
from crewai import Agent, Crew, Process, Task
from web3.types import TxParams
from autotx.utils.agents_config import agents_config
from autotx.utils.ethereum import SafeManager

@dataclass(kw_only=True)
class Config:
    verbose: bool

class AutoTx:
    manager: SafeManager
    agents: list[Agent]
    config: Config = Config(verbose=False)
    transactions: list[TxParams] = []

    def __init__(
        self, manager: SafeManager, agent_factories: list[Callable[['AutoTx'], Agent]], config: Optional[Config]
    ):
        self.manager = manager
        if config:
            self.config = config
        self.agents = [factory(self) for factory in agent_factories]

    def run(self, prompt: str, headless: bool, strict: bool):
        print("Defining goal...", prompt)
       
        agents_information = self.get_agents_information()

        goal = build_goal(prompt, agents_information, headless, strict)

        print("Defining tasks...")
        tasks: list[Task] = define_tasks(goal, agents_information, self.agents)
        Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=self.config.verbose,
            process=Process.sequential,
        ).kickoff()

        self.manager.send_multisend_tx(self.transactions)
        self.transactions.clear()

    def get_agents_information(self) -> str:
        agent_descriptions = []
        for agent_name, agent_details in agents_config.items():
            agent_info = agent_details.model_dump()
            # Find agent with agent_name
            agent = next(filter(lambda a: a.name == agent_name, self.agents), None)

            if not agent:
                continue

            try:
                agent_default_tools: list[StructuredTool] = agent.tools
                tools_available = "\n".join(
                    [
                        f"  - Name: {tool.name}\n  - Description: {tool.description} \n"
                        for tool in agent_default_tools
                    ]
                )
                description = f"Agent name: {agent_name.lower()}\nRole: {agent_info['role']}\nTools available:\n{tools_available}"
                agent_descriptions.append(description)
            except AttributeError:
                raise Exception(f"No default tools defined in agent: {agent_name}")

        agents_information = "\n".join(agent_descriptions)
        return agents_information