from dataclasses import dataclass
import json
from textwrap import dedent
from typing import Optional
from crewai import Agent, Crew, Process, Task
from sage_agent.utils.agents_config import agents_config
from sage_agent.utils.llm import open_ai_llm
import openai
import importlib
from langchain_core.tools import StructuredTool


@dataclass(kw_only=True)
class Config:
    verbose: bool


class Sage:
    agents: list[Agent]
    config: Config = Config(verbose=False)

    def __init__(self, agents: list[Agent], config: Optional[Config]):
        self.agents = agents
        if config:
            self.config = config

    def run(self, prompt: str):
        print("Prompt received...")
        print("Defining tasks...")
        tasks: list[Task] = self.define_tasks(prompt)
        crew = Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=self.config.verbose,
            process=Process.sequential,
            # manager_llm=open_ai_llm,
        )
        return crew.kickoff()

    def define_tasks(self, prompt: str) -> list[Task]:
        #         template = dedent(
        #             """
        # As an expert in decentralized systems, especially Ethereum, you excel at converting user-given prompts into structured tasks
        # for AI agents specializing in direct smart contract interactions; you must explicitly include any user-provided details,
        # such as token addresses and contract addresses, in the corresponding tasks to ensure all necessary information is accounted for and utilized appropriately.

        # Your primary focus is on crafting the necessary calldata for smart contract function calls,
        # with an emphasis on streamlining steps into comprehensive, logically ordered tasks.

        # The allocation of tasks to specific agents is determined by their respective roles, goals, and available tools. as outlined blow:
        # {agents_information}

        # Your approach aims to enhance efficiency by merging steps that naturally complement each other. It is vital to ensure that each task is defined with clarity
        # and precision, especially when it involves encoding transactions or interacting with contracts. Essential details, particularly contract addresses, must be
        # explicitly mentioned in the tasks to prevent omissions.

        # Given the prompt below, your task is to synthesize it into a series of streamlined, ordered tasks. Each task should identify the most appropriate agent
        # or execution, with a clear description, expected output, and context for integration. Remember, tasks involving transaction creation or smart contract interactions must explicitly include contract addresses as part of the task description.

        # When it comes to create the transactions, you must create it in the last step and making
        # sure you share the needed contract addresses to interact with.

        # Please format your response as an array of JSON objects, like so:
        # {{
        #     tasks : [{{
        #         "task": "Concise description of task to be done with details needed given by user"
        #         "agent": "The agent that best fits to execute the task"
        #         "expected_output": str // "Description of expected output for the task"
        #         "context": [int] // Index of tasks that will have their output used as context for this task (Always start from 0), if applicable. Eg. [1, 3] or None
        #         "extra_information": str // Any extra information with description given by the user needed to execute the task, if applicable.
        #     }}]
        # }}

        # This is the prompt: {prompt}

        # Please minimize emphasis on transaction execution/monitoring or gas estimation, as these aspects are managed separately.
        #             """
        #         )

        new_template = dedent(
            """
            Based on the following prompt:
             {prompt}
              
            You must convert instructions into specific tasks with the following JSON format:
            {{
                tasks : [{{
                    "task": "Concise description of task to be done with details needed given by user"
                    "agent": "The agent that best fits to execute the task"
                    "expected_output":"Description of expected output for the task"
                    "context": [int] // Index of tasks that will have their output used as context for this task (Always start from 0), if applicable. Eg. [1, 3] or None
                    "extra_information": Any extra information as string with description given by the user needed to execute the task, if applicable.
                }}]
            }}

            The specific tasks will be created based on the available agents role, goal and available tools:
            {agents_information}
            """
        )
        agent_descriptions = []
        for agent_name, agent_details in agents_config.items():
            agent_info = agent_details.model_dump()
            agent_module = importlib.import_module(f"sage_agent.agents.{agent_name}")

            if agent_name not in [a.name for a in self.agents]:
                continue

            try:
                agent_default_tools: list[StructuredTool] = agent_module.default_tools
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

        formatted_new_template = new_template.format(
            agents_information=agents_information, prompt=prompt
        )

        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": formatted_new_template}],
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
            context: list[Task] = (
                [sanitized_tasks[c] for c in task["context"]] if task["context"] else []
            )

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
                    context=context,
                )
            )

        return sanitized_tasks
