from typing import Optional
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from agents import SageAgents, sage_agent

llm = ChatOpenAI(model="gpt-4-1106-preview")  # type: ignore

agents = SageAgents()
ethereum_agent = agents.ethereum_agent()
erc_20_agent = agents.erc_20_agent()
safe_agent = agents.safe_agent()
bridge_agent = agents.bridge_agent()

sage_agent = sage_agent()

def encode_and_sign():
    class Tasks:
        def get_transfer_transaction():
            return Task(
                description="You must crate a transaction that sends 0.4 Cool Token (token address: 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da) to address 0x0Ce3cC862b26FC643aA8A73D2D30d47EF791941e",
                agent=erc_20_agent,
            )

        def create_transaction_in_safe():
            return Task(
                description="Based on given transaction, you must sign and create a safe transaction",
                agent=safe_agent,
            )

    crew = Crew(
        agents=[erc_20_agent, safe_agent],
        tasks=[
            Tasks.get_transfer_transaction(),
            Tasks.create_transaction_in_safe(),
        ],
        process=Process.sequential,
        full_output=True,
        verbose=True,
    )

    response = crew.kickoff()
    print(response)

class Tasks:
    def get_bridge_transfer_quote(agent: Optional[Agent]):
        return Task(description="I want to send 10 CoolToken (0x57c94aa4a136506d3b88d84473bf3dc77f5b51da) to polygon", agent=agent)

    def create_multiple_transactions(agent: Agent):
        return Task(description="I want to create a transaction in my safe which sends 10 USDC to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 and 5 DAI to 0xAC39C85F4E54797e4909f70a302d9e11E428135D", agent=agent)

def bridge_transaction_create_and_sign_with_crew():
    crew = Crew(
        agents=[erc_20_agent, bridge_agent, ethereum_agent],
        tasks=[Tasks.get_bridge_transfer_quote()],
        verbose=True,
        full_output=True,
        process=Process.hierarchical,
        manager_llm=llm
    )
    response = crew.kickoff()
    print(response)

def bridge_transaction_create_and_sign_with_solo_agent():
    crew = Crew(
        tasks=[Tasks.get_bridge_transfer_quote(sage_agent)],
        verbose=True,
        full_output=True,
    )
    response = crew.kickoff()
    print(response)

def create_multisend():
    crew = Crew(
        tasks=[Tasks.create_multiple_transactions(sage_agent)],
        verbose=True,
        full_output=True,
    )
    response = crew.kickoff()
    print(response)

if __name__ == "__main__":
    # encode_and_sign()
    # bridge_transaction_create_and_sign_with_crew()
    # bridge_transaction_create_and_sign_with_solo_agent()
    create_multisend()