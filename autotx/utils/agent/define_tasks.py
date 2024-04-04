import json
from textwrap import dedent
from crewai import Agent, Task
import openai

def define_tasks(goal: str, agents_information: str, agents: list[Agent]) -> list[Task]:
    template = dedent(
        """
        You are an expert in decomposing and assigning tasks.
        You are good at converting instructions into specific sequential tasks in the following JSON format:
        {{
            tasks : [{{
                "task_id": int, // Task number, which represents the task number, starting from 0
                "task": "Concise description of task to be done with details needed given by user"
                "agent": "The agent that best fits to execute the task"
                "expected_output":"Description of expected output for the task"
                "context": [int] // The task_id that task execution depends on indicates which task_id execution result depends on which task execution depends. Eg. [0, 1] or null if no tasks need to be depended on.
                "extra_information": Any extra information as string with description given by the user needed to execute the task, if applicable.
            }}]
        }}
        Please note that you are only permitted to output json content.

        The specific tasks will be created based on the available agents role, goal and available tools:
        {agents_information}
        
        Please note: You can only output content in json format, and do not output any other content!
        
        You can refer to the following examples:
        Goal: Send 1 ETH from the address 0x5d15311D760511d89cFad67404131cdc155E9FDB to the ENS domain vitalik.eth.
        Output:
        {{
            "tasks": [{{
                "task": "Check the balance of 1 ETH for the address 0x5d15311D760511d89cFad67404131cdc155E9FDB",
                "agent": "send-tokens",
                "expected_output": "A numeric value representing the balance of ETH in the account",
                "context": null,
                "extra_information": "Make sure the balance is at least 1 ETH to proceed with the transaction."
            }}, {{
                "task": "Prepare a transfer transaction of 1 ETH to the ENS domain vitalik.eth",
                "agent": "send-tokens",
                "expected_output": "A message confirming that the ETH transfer transaction has been prepared",
                "context": [0],
                "extra_information": "Use the output of the first task to ensure there is enough balance before proceeding."
            }}]
        }}
        
        Goal: Execute a swap from ETH to 100 USDC for the user's address 0x5d15311D760511d89cFad67404131cdc155E9FDB
        Output:
        {{
            "tasks": [
                {{
                    "task": "Get current ETH balance of the user",
                    "agent": "send-tokens",
                    "expected_output": "Current ETH balance of 0x5d15311D760511d89cFad67404131cdc155E9FDB",
                    "context": null,
                    "extra_information": "Use Get ETH balance tool to check current ETH balance of user's address."
                }},
                {{
                    "task": "Calculate ETH amount needed to swap for 100 USDC",
                    "agent": "swap-tokens",     
                    "expected_output": "The amount of ETH needed to execute a swap to receive 100 USDC",
                    "context": null,
                    "extra_information": "Assuming the swap service or agent has the capability to estimate, based on existing market rates, how much ETH is required."
                }},
                {{
                    "task": "Build transactions needed to execute the swap from ETH to 100 USDC",
                    "agent": "swap-tokens",
                    "expected_output": "Transactions prepared for swapping ETH to exactly 100 USDC",
                    "context": [2],
                    "extra_information": "Use the calculated ETH amount from the previous step to prepare the necessary transactions for the swap, ensuring that the exact_input is set to True since we want to receive an exact amount of USDC."
                }}
            ]
        }}
        
        Goal: First, swap Ethereum (ETH) to 0.05 Wrapped Bitcoin (WBTC), ensuring the right amount of ETH is swapped for exactly 0.05 WBTC. After successfully swapping to WBTC, proceed to swap WBTC to 1000 USD Coin (USDC), making sure to receive exactly 1000 USDC from the swap. Following these swaps, transfer 50 USDC to the Ethereum Name Service (ENS) domain 'vitalik.eth'.
        Output:
        {{
            "tasks": [
                {{
                    "task": "Swap the required amount of Ethereum (ETH) for exactly 0.05 Wrapped Bitcoin (WBTC)",
                    "agent": "swap-tokens",
                    "expected_output": "A successful swap transaction from ETH to WBTC where the user ends up with exactly 0.05 WBTC",
                    "context": null,
                    "extra_information": "Use the exact_output mode for the swap, ensuring the exact amount of 0.05 WBTC is received. Calculate the required ETH amount based on current market rates."
                }},
                {{
                    "task": "Swap Wrapped Bitcoin (WBTC) for 1000 USD Coin (USDC)",
                    "agent": "swap-tokens",
                    "expected_output": "A successful swap transaction from WBTC to USDC where the user ends up with exactly 1000 USDC",
                    "context": null,
                    "extra_information": "Use the exact_output mode for the swap, ensuring the exact amount of 1000 USDC is received."
                }},
                {{
                    "task": "Transfer 50 USDC to the Ethereum Name Service (ENS) domain 'vitalik.eth'",
                    "agent": "send-tokens",
                    "expected_output": "A confirmation message that the transaction to transfer 50 USDC to 'vitalik.eth' has been prepared",
                    "context": null,
                    "extra_information": "Ensure to use the USDC token symbol in the transfer command and verify the correct ENS domain name before executing the transfer."
                }}
            ]
        }}
        
        OK, start now!
        Please note: You can only output content in json format, and do not output any other content!
        Goal: {goal}
        Output:
        """
    )

    formatted_template = template.format(
        agents_information=agents_information, goal=goal
    )

    # TODO: Improve how we pass messages. We should use system role
    response = openai.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": formatted_template}],
    )
    response = response.choices[0].message.content
    if not response:
        raise Exception("Bad response from OpenAI API for defining tasks.")

    print("Tasks", response)

    return sanitize_tasks_response(response, agents)

def sanitize_tasks_response(response: str, agents: list[Agent]) -> list[Task]:
    tasks = json.loads(response)["tasks"]
    sanitized_tasks: list[Task] = []
    for task in tasks:
        context: list[Task] = (
            [sanitized_tasks[c] for c in task["context"]] if task["context"] else []
        )

        get_agent_by_name = lambda a: a.name.lower() == task["agent"].lower()
        agent = next(filter(get_agent_by_name, agents), None)
        description = task["task"]
        if not agent:
            raise Exception(f"Agent {task['agent']} not found.", task)

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