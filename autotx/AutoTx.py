from typing import Optional, Callable
from dataclasses import dataclass
from typing import Optional
from crewai import Agent, Crew, Process, Task
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.agent.build_goal import build_goal
from autotx.utils.agent.define_tasks import define_tasks
from langchain_core.tools import StructuredTool
from crewai import Agent, Crew, Process, Task
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.llm import open_ai_llm

@dataclass(kw_only=True)
class Config:
    verbose: bool

class AutoTx:
    manager: SafeManager
    agents: list[Agent]
    config: Config = Config(verbose=False)
    transactions: list[PreparedTx] = []
    network: NetworkInfo

    def __init__(
        self, manager: SafeManager, network: NetworkInfo, agent_factories: list[Callable[['AutoTx'], Agent]], config: Optional[Config]
    ):
        self.manager = manager
        self.network = network
        if config:
            self.config = config
        self.agents = [factory(self) for factory in agent_factories]

    def run(self, prompt: str, non_interactive: bool):
        print(f"Defining goal for prompt: '{prompt}'")
       
        agents_information = self.get_agents_information()

        goal = build_goal(prompt, agents_information, self.manager.address, non_interactive)

        print(f"Defining tasks for goal: '{goal}'")
        tasks: list[Task] = define_tasks(goal, agents_information, self.agents)
   
        self.run_for_tasks(tasks, non_interactive)

    def run_for_tasks(self, tasks: list[Task], non_interactive: bool):
        print(f"Running tasks...")
        Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=self.config.verbose,
            process=Process.sequential,
            function_calling_llm=open_ai_llm,
        ).kickoff()

        self.manager.send_tx_batch(self.transactions, require_approval=not non_interactive)
        self.transactions.clear()

    def get_agents_information(self) -> str:
        agent_descriptions = []
        for agent in self.agents:
            agent_default_tools: list[StructuredTool] = agent.tools
            tools_available = "\n".join(
                [
                    f"  - Name: {tool.name}\n  - Description: {tool.description} \n"
                    for tool in agent_default_tools
                ]
            )
            description = f"Agent name: {agent.name}\nRole: {agent.role}\nTools available:\n{tools_available}"
            agent_descriptions.append(description)

        agents_information = "\n".join(agent_descriptions)
        return agents_information