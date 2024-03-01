from typing import Optional
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from agents import SageAgents, sage_agent

llm = ChatOpenAI(model="gpt-4-1106-preview")  # type: ignore

agents = SageAgents()
# ethereum_agent = agents.ethereum_agent()
erc_20_agent = agents.erc_20_agent()
safe_agent = agents.safe_agent()
bridge_agent = agents.bridge_agent()
uniswap_agent = agents.uniswap_agent()

sage_agent = sage_agent()


def encode_and_sign_sequential():
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


def encode_and_sign_hierarchical():
    crew = Crew(
        agents=[erc_20_agent, safe_agent],
        tasks=[
            Task(
                description="Create a transaction that sends 0.4 Cool Token (token address: 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da) to address 0x0Ce3cC862b26FC643aA8A73D2D30d47EF791941e; then, sign it and create a safe transaction"
            )
        ],
        process=Process.hierarchical,
        manager_llm=llm,
        verbose=True,
    )

    response = crew.kickoff()
    print(response)






    def swap_token():
        return Task(description="I want to swap 10 USDC to DAI", agent=uniswap_agent)




def swap_and_transfer_through_safe_with_hierarchical():
    #     task = Task(description="""
    # I want to swap 10 DAI to USDC and then transfer 3 USDC to 0x61FfE691821291D02E9Ba5D33098ADcee71a3a17
    # in the same transaction; create and sign a transaction contaning these actions in my safe with address 0xSAFE
    # """)
    def multiple_tasks():
        swap_task = Task(
            description="I want to swap 10 DAI to USDC",
            expected_output="Calldata to execute swap transaction",
        )
        transfer_task = Task(
            description="I want to transfer 3 USDC to 0x61FfE691821291D02E9Ba5D33098ADcee71a3a17",
            expected_output="Calldata to execute transfer transaction",
        )
        create_and_sign_multisend = Task(
            description="Create and sign a multisend transaction that contains the swap and transfer transactions in my safe with address 0x5afe",
            context=[swap_task, transfer_task],
        )

        return [swap_task, transfer_task, create_and_sign_multisend]

    crew = Crew(
        agents=[uniswap_agent, safe_agent, erc_20_agent],
        tasks=multiple_tasks(),
        verbose=True,
        process=Process.hierarchical,
        manager_llm=llm,
    )
    response = crew.kickoff()
    print(response)


def swap_and_transfer_through_safe_with_sequential():
    def multiple_tasks():
        swap_task = Task(
            description="I want to swap 10 DAI to USDC",
            expected_output="Calldata to execute swap transaction",
            agent=uniswap_agent,
        )
        transfer_task = Task(
            description="I want to transfer 3 USDC to 0x61FfE691821291D02E9Ba5D33098ADcee71a3a17",
            expected_output="Calldata to execute transfer transaction",
            agent=erc_20_agent,
        )
        create_and_sign_multisend = Task(
            description="Create and sign a multisend transaction that contains the swap and transfer transactions in my safe with address 0x5afe",
            agent=safe_agent,
            context=[swap_task, transfer_task],
        )

        return [swap_task, transfer_task, create_and_sign_multisend]

    crew = Crew(
        agents=[uniswap_agent, safe_agent, erc_20_agent],
        tasks=multiple_tasks(),
        verbose=True,
    )
    response = crew.kickoff()
    print(response)


if __name__ == "__main__":
    # encode_and_sign_sequential()
    # encode_and_sign_hierarchical()
    # bridge_transaction_create_and_sign_with_crew()
    # bridge_transaction_create_and_sign_with_solo_agent()
    # create_multisend()
    # create_multisend_in_crew()
    # swap_dai_to_usdc()
    swap_and_transfer_through_safe_with_hierarchical()
    # swap_and_transfer_through_safe_with_sequential()
