from dataclasses import dataclass
from typing import Optional
from crewai import Agent, Crew, Process, Task
from sage_agent.utils.llm import open_ai_llm


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
        tasks: list[Task] = self.sanitize_prompt(prompt)
        crew = Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=self.config.verbose,
            process=Process.hierarchical,
            manager_llm=open_ai_llm,
        )
        return crew.kickoff()

    def sanitize_prompt(self, prompt: str) -> list[Task]:
        #TODO: Implement this
        return [Task(description=prompt)]
