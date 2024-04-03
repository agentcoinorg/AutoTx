import json
from autotx.patch import patch_langchain
from autotx.utils.agent.define_tasks import sanitize_tasks_response
from autotx.utils.ethereum import get_erc20_balance
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.get_eth_balance import get_eth_balance

patch_langchain()

def test_send_tokens_agent(configuration, auto_tx, test_accounts):
    (_, _, client, _) = configuration
    receiver = test_accounts[0]
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

def test_send_tokens_agent_with_check_eth(configuration, auto_tx, test_accounts):
    (_, _, client, _) = configuration

    receiver = test_accounts[0]
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

def test_send_tokens_agent_with_check_erc20(configuration, auto_tx, usdc, test_accounts):
    (_, _, client, _) = configuration

    receiver = test_accounts[0]
    balance = get_eth_balance(client.w3, receiver)
    assert balance == 0

    tasks_json = {
        "tasks": [
            {
                "task": f"Check the balance of USDC for address {auto_tx.manager.address}.",
                "agent": "send-tokens",
                "expected_output": "A floating-point number indicating the balance of USDC at the given address. This will confirm if the address has at least 10 USDC to send.",
                "context": None,
                "extra_information": "It is crucial to verify that the sender has enough USDC before attempting to prepare the transfer transaction."
            },
            {
                "task": f"Prepare a transfer transaction for sending 10 USDC from address {auto_tx.manager.address} to receiver address {receiver}.",
                "agent": "send-tokens",
                "expected_output": "A message confirming that the transfer transaction for 10 USDC to the specified receiver address has been prepared.",
                "context": [0],
                "extra_information": "This transaction is dependent on confirming that the sender's balance is sufficient as checked in the previous task."
            }
        ]
    }
    tasks = sanitize_tasks_response(json.dumps(tasks_json), auto_tx.agents)

    balance = get_erc20_balance(client.w3, usdc, receiver)

    auto_tx.run_for_tasks(tasks, non_interactive=True)

    new_balance = get_erc20_balance(client.w3, usdc, receiver)

    assert balance + 10 == new_balance
