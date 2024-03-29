import json
from autotx.patch import patch_langchain
from autotx.utils.agent.define_tasks import sanitize_tasks_response
from autotx.utils.ethereum import get_erc20_balance
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.get_eth_balance import get_eth_balance

patch_langchain()

def test_send_tokens_agent(configuration, auto_tx):
    (_, _, client, _) = configuration
    receiver = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)
    balance = get_eth_balance(client.w3, receiver)
    assert balance == 0

    tasks_json = {
        "tasks": [
            {
                "task": f"Prepare a transaction to send 1 ETH from address {auto_tx.manager.address} to the address {receiver}.",
                "agent": "send-tokens",
                "expected_output": "A confirmation message that the transaction to send 1 ETH has been prepared.",
                "context": None,
                "extra_information": "This transaction must be prepared after confirming there is enough of a balance to proceed."
            }
        ]
    }
    tasks = sanitize_tasks_response(json.dumps(tasks_json), auto_tx.agents)

    auto_tx.run_for_tasks(tasks, non_interactive=True)

    balance = get_eth_balance(client.w3, receiver)
    assert balance == 1

def test_send_tokens_agent_with_check(configuration, auto_tx):
    (_, _, client, _) = configuration
    receiver = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)
    balance = get_eth_balance(client.w3, receiver)
    assert balance == 0

    tasks_json = {
        "tasks": [
            {
                "task": f"Check the ETH balance of the user's address {auto_tx.manager.address}.",
                "agent": "send-tokens",
                "expected_output": "The balance of ETH in the user's address.",
                "context": None,
                "extra_information": "This check is to ensure the user has enough ETH to send 1 ETH to the specified address."
            },
            {
                "task": f"Transfer 1 ETH from the user's address {auto_tx.manager.address} to the address {receiver}.",
                "agent": "send-tokens",
                "expected_output": "Message confirming that the ETH transfer transaction has been prepared.",
                "context": [0],
                "extra_information": "Proceed with this transfer only if the balance checked from the first task is sufficient to send 1 ETH and cover the transaction fees."
            }
        ]
    }
    tasks = sanitize_tasks_response(json.dumps(tasks_json), auto_tx.agents)

    auto_tx.run_for_tasks(tasks, non_interactive=True)

    balance = get_eth_balance(client.w3, receiver)
    assert balance == 1

def test_send_tokens_agent_with_check2(configuration, auto_tx, mock_erc20):
    (_, _, client, _) = configuration
    receiver = ETHAddress("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", client.w3)
    balance = get_eth_balance(client.w3, receiver)
    assert balance == 0

    tasks_json = {
        "tasks": [
            {
                "task": f"Check the balance of TTOK for address {auto_tx.manager.address}.",
                "agent": "send-tokens",
                "expected_output": "A floating-point number indicating the balance of TTOK at the given address. This will confirm if the address has at least 10 TTOK to send.",
                "context": None,
                "extra_information": "It is crucial to verify that the sender has enough TTOK before attempting to prepare the transfer transaction."
            },
            {
                "task": f"Prepare a transfer transaction for sending 10 TTOK from address {auto_tx.manager.address} to receiver address {receiver}.",
                "agent": "send-tokens",
                "expected_output": "A message confirming that the transfer transaction for 10 TTOK to the specified receiver address has been prepared.",
                "context": [0],
                "extra_information": "This transaction is dependent on confirming that the sender's balance is sufficient as checked in the previous task."
            }
        ]
    }
    tasks = sanitize_tasks_response(json.dumps(tasks_json), auto_tx.agents)

    balance = get_erc20_balance(client.w3, mock_erc20, receiver)

    auto_tx.run_for_tasks(tasks, non_interactive=True)

    new_balance = get_erc20_balance(client.w3, mock_erc20, receiver)

    assert balance + 10 == new_balance
