from dataclasses import dataclass
import json
from textwrap import dedent
from typing import Optional
import typing
from crewai import Agent, Crew, Process, Task
from autotx.utils.agents_config import agents_config
import openai
from langchain_core.tools import StructuredTool
from web3.types import TxParams

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
        self, manager: SafeManager, agent_factories: list[typing.Callable[['AutoTx'], Agent]], config: Optional[Config]
    ):
        self.manager = manager
        if config:
            self.config = config
        self.agents = [factory(self) for factory in agent_factories]

    def run(self, prompt: str):
        print("Defining tasks...")
        tasks: list[Task] = self.define_tasks(prompt)
        Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=self.config.verbose,
            process=Process.sequential,
        ).kickoff()

        self.manager.send_multisend_tx(self.transactions)
        self.transactions.clear()

    def define_tasks(self, prompt: str) -> list[Task]:
        template = dedent(
            """
            Based on the following prompt: {prompt}

            You must convert instructions into specific tasks

            The response must have the following format:
            ```json
            {{
                tasks : [{{
                    "task": "Concise description of task to be done with all needed details"
                    "agent": "The agent that best fits to execute the task"
                    "expected_output":"Description of expected output for the task"
                }}]
            }}
            ```

            The specific tasks will be created based on the available agents role, goal and available tools:
            {agents_information}
            """
        )
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

        formatted_template = template.format(
            agents_information=agents_information, prompt=prompt
        )

        # TODO: Improve how we pass messages. We should use system role
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": formatted_template}],
        )
        response = response.choices[0].message.content
        print(response)
        if not response:
            # TODO: Handle bad response
            pass

        return self.sanitize_tasks_response(response)

    def sanitize_tasks_response(self, response: str) -> list[Task]:
        tasks = json.loads(response)["tasks"]
        sanitized_tasks: list[Task] = []
        for task in tasks:
            get_agent_by_name = lambda a: a.name == task["agent"]
            agent = next(filter(get_agent_by_name, self.agents), None)
            description = task["task"]

            if task["extra_information"]:
                description += "\n" + task["extra_information"]

            sanitized_tasks.append(
                Task(
                    description=description,
                    agent=agent,
                    expected_output=task["expected_output"],
                )
            )

        return sanitized_tasks
