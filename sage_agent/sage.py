from dataclasses import dataclass
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
        tasks: list[Task] = self.define_tasks(prompt)
        crew = Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=self.config.verbose,
            process=Process.hierarchical,
            manager_llm=open_ai_llm,
        )
        return crew.kickoff()

    def define_tasks(self, prompt: str) -> list[Task]:
        template = dedent(
            """
            You are an expert in decentralized systems, especially Ethereum.
            Your primary experience lies in converting user-given prompts into concrete tasks for AI agents that specialize
            in direct interactions with smart contracts on Ethereum. The focus is on preparing the necessary calldata for smart contract function calls,
            emphasizing the consolidation of steps into comprehensive tasks whenever practical.

            The decision on which agent delegate tasks to will be based on each agent's role, goal and available tools, as outlined below:
            {agents_information}


            Your approach should streamline the process by combining steps that naturally fit together,
            aiming for efficiency without sacrificing clarity or detail.

            Given the following prompt, please analyze and synthesize it into a series of streamlined tasks.
            For each task, identify the most suitable agent for execution. Clearly describe the task, specify the expected output,
            and note any tasks that provide context. Aim to consolidate steps into single tasks where feasible,
            especially if they involve sequential actions by the same agent.
            Please format your response as an array of JSON objects, like so:

            {{
                tasks : [{{
                    "task": "A clear, concise statement of what the task entails",
                    "agent": "The agent that best fits to execute the task",
                    "expected_output": "Clear and detailed definition of expected output for the task, if applicable",
                    "context": "Index of tasks that will have their output used as context for this task, if applicable"
                }}]
            }}


            This is the prompt: {prompt}

            Please minimize emphasis on transaction execution/monitoring or gas estimation, as these aspects are managed separately by the system.
            Instead, focus on preparing transaction data and other preparatory steps that can logically be grouped together
            """
        )
        agent_descriptions = []
        for agent_name, agent_details in agents_config.items():
            agent_info = agent_details.model_dump()
            agent_module = importlib.import_module(f"sage_agent.agents.{agent_name}")

            try:
                agent_default_tools: list[StructuredTool] = agent_module.default_tools
                tools_available = "\n".join(
                    [
                        f"- Name: {tool.name} - Description: {tool.description} \n"
                        for tool in agent_default_tools
                    ]
                )
                description = f"{agent_name}: Role - {agent_info['role']}, Goal - {agent_info['goal']}. Tools available: {tools_available}"
                agent_descriptions.append(description)
            except AttributeError:
                raise Exception(f"No default tools defined in agent: {agent_name}")

        agents_information = "\n".join(agent_descriptions)

        formatted_template = template.format(
            agents_information=agents_information, prompt=prompt
        )

        response = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": formatted_template}],
        )
        print(response.choices[0].message.content)
        return [Task(description=prompt)]
