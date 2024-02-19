from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.ethereum import EthereumTools
from tools.erc20 import Erc20Tools

llm = ChatOpenAI(model="gpt-4-1106-preview")  # type: ignore

agent = Agent(
    role="Ethereum assistant",
    goal="Interact with ethereum blockchain",
    backstory="""
You're proefficient in the understanding of how to interact with ethereum
""",
    tools=[
        EthereumTools.get_balance,
        EthereumTools.send_transaction,
        Erc20Tools.encode,
        Erc20Tools.get_balance,
        Erc20Tools.get_information
    ],
    llm=llm,
    function_calling_llm=llm,
    verbose=True,
)


get_balance_prompt = (
    "Get the balance from address 0x61FfE691821291D02E9Ba5D33098ADcee71a3a17"
)
send_transaction_prompt = (
    "I want to send 0.2 eth to 0x61FfE691821291D02E9Ba5D33098ADcee71a3a17"
)

send_erc20_prompt = (
    "I want to transfer 0.4 Cool Token (token address: 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da) to address 0x0Ce3cC862b26FC643aA8A73D2D30d47EF791941e"
)

if __name__ == "__main__":
    print("## Welcome to ethereum agent :)")
    task = Task(description=send_erc20_prompt, agent=agent)
    response = task.execute()
    print(response)
