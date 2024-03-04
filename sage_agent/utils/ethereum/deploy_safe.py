from eth_account import Account
from eth_typing import URI
from gnosis.eth import EthereumClient
from gnosis.safe import Safe

from sage_agent.utils.ethereum.constants import MASTER_COPY_ADDRESS

SAFE_ADDRESS_FILE = "./cache/safe.txt"

def deploy_safe(account: Account, rpc_url: str, signers: list[str], threshold: int) -> tuple[str, Safe]:
    existing_address = get_existing_safe_address()

    if existing_address:
        return existing_address, Safe(existing_address, EthereumClient(URI(rpc_url))) 
   
    client = EthereumClient(URI(rpc_url))
    
    tx = Safe.create(
        client, 
        account,
        MASTER_COPY_ADDRESS,
        signers,
        threshold
    )

    if not tx.contract_address:
        raise ValueError("Safe contract address is not set")
    
    print("Deployed safe to: ", tx.contract_address)

    save_safe_address(tx.contract_address)

    return tx.contract_address, Safe(tx.contract_address, client)

def get_existing_safe_address() -> str:
    safe_address = ""

    try:
        with open(SAFE_ADDRESS_FILE, "r") as file:
            safe_address = file.read().strip()  # Use strip() to remove newline characters
    except FileNotFoundError:
        print(SAFE_ADDRESS_FILE + " not found, a new Safe will be deployed.")
    except Exception as e:
        print(f"An error occurred while reading " + SAFE_ADDRESS_FILE + ": {e}")
        raise

    return safe_address

def save_safe_address(safe_address: str) -> None:
    with open(SAFE_ADDRESS_FILE, "w") as file:
        file.write(safe_address)