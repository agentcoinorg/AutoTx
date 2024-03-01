from dataclasses import dataclass
from crewai import Agent, Crew, Process, Task
from sage_agent.utils.llm import open_ai_llm
# import json

@dataclass(kw_only=True)
class Config:
    verbose: bool

class Sage:
    agents: list[Agent]
    config: Config = { "verbose": False }

    def __init__(self, agents: list[Agent], config: Config | None):
        # self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
        # self.OpenAIGPT4 = ChatOpenAI(model="gpt-4-turbo-preview")
        self.agents = agents

    def run(self, prompt: str):
        # config = json.dumps(
        #     {
        #         "agents": [
        #             {
        #                 "role": "Senior Researcher",
        #                 "goal": "Make the best research and analysis on content about AI and AI agents",
        #                 "backstory": "You're an expert researcher, specialized in technology, software engineering, AI and startups. You work as a freelancer and is now working on doing research and analysis for a new customer.",
        #             },
        #             {
        #                 "role": "Senior Writer",
        #                 "goal": "Write the best content about AI and AI agents.",
        #                 "backstory": "You're a senior writer, specialized in technology, software engineering, AI and startups. You work as a freelancer and are now working on writing content for a new customer.",
        #             },
        #         ],
        #         "tasks": [
        #             {
        #                 "description": "Give me a list of 5 interesting ideas to explore for na article, what makes them unique and interesting.",
        #                 "agent": "Senior Researcher",
        #             },
        #             {
        #                 "description": "Write a 1 amazing paragraph highlight for each idead that showcases how good an article about this topic could be, check references if necessary or search for more content but make sure it's unique, interesting and well written. Return the list of ideas with their paragraph and your notes.",
        #                 "agent": "Senior Writer",
        #             },
        #         ],
        #     }
        # )
        # TODO: Sanitize prompt and create specialized tasks
        crew = Crew(
            # config=config,
            agents=self.agents,
            tasks=[Task(description=prompt)],
            verbose=True,
            process=Process.hierarchical,
            manager_llm=open_ai_llm,
        )
        return crew.kickoff()
        pass

