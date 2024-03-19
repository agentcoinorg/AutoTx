# AutoTx

AutoTx is a tool that allows users to automate their interactions with blockchains. 
To accomplish this, it uses autonomous LLM-based agents to interpret the user's intent and execute transactions through a gnosis safe.
AutoTx has its own wallet which it uses as a signer for proposing or executing transactions through a shared gnosis safe.

This project is build on top of crew-ai, langchain, web3.py, gnosis safe and openai.

## Getting Started
Make sure you have the following:
- [python](https://www.python.org/downloads/)
- [poetry](https://python-poetry.org/docs/#installation)
- [docker](https://www.docker.com/)

### Installation:
1. Clone the repository

2. Create a `.env` and copy and configure content from the `.env.example` file. The description of the different environment variables can be found below.

4. Start poetry shell and install dependencies
> poetry shell  
> poetry install

5. Start local environment
> poetry run start-env

The above command will start a local blockchain node that is a fork of the `FORK_RPC_URL` node. 
Addresses and private keys of test accounts that are loaded up with Ether will be printed to the console.

Make sure to copy a private key and set it as the `USER_PRIVATE_KEY` environment variable or just use the default one from the `.env.example` file.

### Environment variables:
- `USER_PRIVATE_KEY` - The private key of the user's wallet. Used for loading up other accounts with Ether.
- `RPC_URL` - The URL of the blockchain node. Use `http://127.0.0.1:8545/` if connecting to a local node started by `poetry run start-env`
- `OPENAI_API_KEY` - The OPENAI API key. Used for interacting with the OpenAI API.
- `FORK_RPC_URL` - The URL of the blockchain node to fork from. Used by `poetry run start-env` to start a local fork of the blockchain. You can use infura or alchemy for this.

### Run:
To run AutoTx, use the following command:
> poetry run ask

The above command will start the AutoTx agent and prompt you to input a prompt.

To run AutoTx with a specific prompt:
> poetry run ask --prompt "I want to send 1 ETH to 0x1234"

To connect to an existing safe:  
> poetry run safe connect --address 0x1234

In order for the agent to be able to execute or propose transactions, the agent account needs to be added as a signer to the safe.  
To create a new agent account:  
> poetry run agent create  

To display the address and info of the agent account:  
> poetry run agent info  

If you want to delete the agent account:  
> poetry run agent delete

## Testing
Tests are located in the `autotx/tests` directory.

To run all tests, use the following command:
> poetry run pytest -s

To run all tests in specific file, use the following command:
> poetry run pytest -s ./autotx/tests/test_swap.py

To run a specific test, use the following command:
> poetry run pytest -s ./autotx/tests/test_swap.py::test_swap

## How it works
When you run AutoTx, it will prompt you to input a prompt.
The prompt is then sent to the OpenAI API, which turns the prompt into a list of crew-ai tasks.
Tasks are then passed to crew-ai which start executing them one by one with the use of pre-defined agents.
The agents are responsible for interpreting the user's intent and executing the tasks.
The agents use the gnosis safe to propose or execute transactions.
Each agent has a set of tools (functions) at it's disposal.
Agents can be found in the `autotx/agents` directory.
List of current agents:
- SendTokensAgent
- SwapTokensAgent

## How to customize

### Adding tools to existing agents
You can find the agents in the `autotx/agents` directory.
There are two ways of adding tools to an agent:

#### With the `@tool` decorator:
```python
@tool("Name of the tool")
def my_tool(param1: str, param2: int) -> int:
    """
    This is the description of the tool

    :param param1: str, description of param1
    :param param2: int, description of param2

    :result name_of_result: int, description of the result
    """
    return 0
```
Use the above when you want a quick and simple way of adding a tool to an agent.
Then add the tool to the agent:
```python
 super().__init__(
    **config,
    tools=[
        my_tool,
    ],
    ...
)
```

#### With a custom tool class:
```python
class MyTool(BaseTool):
    name: str = "Name of the tool"
    description: str = "Description of the tool"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        super().__init__()

    def _run(self, param1: str) -> str:
        """
        :param param1: str, description of param1

        :return name_of_result: str, description of the result
        """
        return "some string"
```
Use the above when you need to add state and/or dependencies to the tool.
Then add the tool to the agent:
```python
super().__init__(
    **config,
    tools=[MyTool()],
    ...
)
```

### Adding agents
To add a new agent first add a new entry in ./autotx/config/agents.json. Fill in the role, goal and backstory.
Then create a new file in the `autotx/agents` directory and add a new class that inherits from the `Agent` class.
Example: 
```python
class MyAgent(Agent):
    name: str

    def __init__(self):
        name = "my_agent_name"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[
                // Tools go here
            ],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name,
        )
```
AutoTx class accepts a list of agents as an argument, so be sure to add the new agent to the list.
Go to `autotx/main.py` and add the new agent to the list of agents:
```python
    my_agent = MyAgent()
    autotx = AutoTx(..., [..., my_agent], ...)
```

### Adding tests
To add a new test, create a new file in the `autotx/tests` directory.

Then create a new test function.

Example: `def test_hello_world(configuration):`

Each test function needs to start with `test_` and accept a `configuration` fixture as an argument.

The `configuration` fixture is a tuple that consists of the following: (user, agent, client, manager).
Where user is the user's account, agent is the agent's account, client is the EthereumClient instance and manager is the SafeManager instance.

The fixture will take care of creating those accounts and instances for you as well as deploying a gnosis safe.

## Roadmap

### v0.1.0 (Current)
- [x] Start local environment
- [x] Create a gnosis safe
- [x] Send Ether and ERC20 tokens
- [x] Swap ERC20 tokens
- [] Support existing safe
- [] Fetch token addresses from a third-party API

### v0.2.0

