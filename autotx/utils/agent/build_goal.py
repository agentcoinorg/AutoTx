import json
import os
from textwrap import dedent
import typing

import openai

from autotx.utils.ethereum.eth_address import ETHAddress

class GoalResponse:
    goal: str
    type: str = "goal"

    def __init__(self, goal: str):
        self.goal = goal

class MissingInfoResponse:
    message: str
    type: str = "missing_info"

    def __init__(self, message: str):
        self.message = message

class InvalidPromptResponse:
    message: str
    type: str = "unsupported"

    def __init__(self, message: str):
        self.message = message

DefineGoalResponse = typing.Union[GoalResponse, MissingInfoResponse, InvalidPromptResponse]

def get_persona(smart_account_address: ETHAddress) -> str:
    return dedent(
        f"""
        You are an AI assistant that helps the user define goals and tasks for your agents. 
        You can analyze prompts and provide the user with a goal to be executed by the agents.
        When dealing with Ethereum transactions, assume the following is the user's address: {smart_account_address}
        """
    )

def build_goal(prompt: str, agents_information: str, smart_account_address: ETHAddress, non_interactive: bool) -> str:
    response: DefineGoalResponse | None = None
    chat_history = f"User: {prompt}"

    while True:
        response = analyze_user_prompt(chat_history, agents_information, smart_account_address)
        if response.type == "missing_info":
            autotx_message = f"Missing information: {response.message}"

            if non_interactive:
                raise Exception(autotx_message)
            else:
                chat_history += "\nYou: " + autotx_message + "\nUser: " + input(f"{autotx_message}\nInput response: ")

        elif response.type == "unsupported":
            autotx_message = f"Unsupported prompt: {response.message}"

            if non_interactive:
                raise Exception(autotx_message)
            else:
                chat_history = "User: " + input(f"{autotx_message}\nNew prompt: ")

        elif response.type == "goal":
            return response.goal

def analyze_user_prompt(chat_history: str, agents_information: str, smart_account_address: ETHAddress) -> DefineGoalResponse:
    template = dedent(
        """
        You are a task assignment expert. You are good at analyzing the user's chat records to complete the task goals and conditions represented in the user's chat records.
        You must analyze the prompt and define a goal to be executed by the agents.
        If the prompt is not clear or missing information, you MUST ask for more information.
        If the prompt is invalid, unsupported or outside the scope of the agents, you MUST ask for a new prompt.
        Always ensure you have all the information needed to define the goal that can be executed without prior context.
        When dealing with Ethereum transactions, assume the following is the user's address: {smart_account_address}
        
        The available agents and tools:
        {agents_information}

        Respond ONLY in one of three of the following JSON formats:
        
        {{
            "type": "goal",
            "goal": "The detailed goal here. No need to mention specific agents or tools."
        }}
        
        {{
            "type": "missing_info",
            "message": "The information that is missing here"
        }}
        
        {{
            "type": "unsupported",
            "message": "Reason why the prompt is unsupported here"
        }}
        
        Please note: You can only output content in json format, and do not output any other content!
        
        You can refer to the following examples:
        Chat History: User: Swap ETH to 0.05 WBTC, then swap WBTC to 1000 USDC, and finally send 50 USDC to vitalik.eth
        Output: 
        {{
            "type": "goal",
            "goal": "First, swap Ethereum (ETH) to 0.05 Wrapped Bitcoin (WBTC), ensuring the right amount of ETH is swapped for exactly 0.05 WBTC. After successfully swapping to WBTC, proceed to swap WBTC to USD Coin (USDC), making sure to receive exactly 1000 USDC from the swap. Following these swaps, transfer 50 USDC to the Ethereum Name Service (ENS) domain 'vitalik.eth'."
        }}
        
        Chat History: User: Send 1 ETH to vitalik.eth
        Output: 
        {{
            "type": "goal",
            "goal": "Send 1 ETH from the address 0x5d15311D760511d89cFad67404131cdc155E9FDB to the ENS domain vitalik.eth."
        }}
        
        Chat History: User: Buy 100 USDC with ETH
        Output: 
        {{
            "type": "goal",
            "goal": "Execute a swap from ETH to 100 USDC for the user's address 0x5d15311D760511d89cFad67404131cdc155E9FDB"
        }}
        
        OK, start now!
        Please note: You can only output content in json format, and do not output any other content!
        Chat History: {chat_history}
        Output:
        """
    )

    formatted_template = template.format(
        agents_information=agents_information, chat_history=chat_history, smart_account_address=smart_account_address
    )

    response = openai.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4-turbo-preview"),
        response_format={"type": "json_object"},
        messages=[
            { "role": "system", "content": get_persona(smart_account_address) },
            { "role": "user", "content": formatted_template }
        ],
    )
    response = response.choices[0].message.content
    if not response:
        # TODO: Handle bad response
        pass

    # Only keep the JSON part of the response
    bracket_index = response.find('{')
    bracket_last = response.rfind('}')
    response = response[bracket_index:bracket_last + 1]

    return parse_analyze_prompt_response(response)

def parse_analyze_prompt_response(response: str) -> DefineGoalResponse:
    response = json.loads(response)
    if response["type"] == "goal":
        return GoalResponse(response["goal"])
    elif response["type"] == "missing_info":
        return MissingInfoResponse(response["message"])
    elif response["type"] == "unsupported":
        return InvalidPromptResponse(response["message"])
    else:
        raise Exception("Invalid response type")