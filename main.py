import os
import click
from dotenv import load_dotenv
from eth_account import Account
from eth_typing import URI
from gnosis.eth import EthereumClient
from gnosis.safe.multi_send import MultiSend, MultiSendTx, MultiSendOperation
from gnosis.safe.safe_tx import SafeTx
from gnosis.eth.multicall import Multicall
from gnosis.safe import SafeOperation
from web3 import Web3
from web3.types import TxParams
from web3.middleware import construct_sign_and_send_raw_middleware

from utils import deploy_multicall, deploy_safe_with_create2, generate_agent_account, get_eth_balance, send_eth
from utils.constants import MULTI_SEND_ADDRESS
from utils.mock_erc20 import MOCK_ERC20_ABI, MOCK_ERC20_BYTECODE

load_dotenv()

def deploy_mock_erc20(web3: Web3, account: Account) -> str:
    web3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

    MockERC20 = web3.eth.contract(abi=MOCK_ERC20_ABI, bytecode=MOCK_ERC20_BYTECODE)

    tx_hash = MockERC20.constructor().transact({"from": account.address})

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return receipt.contractAddress

def transfer_erc20(web3: Web3, token_address: str, from_account: Account, to: str, value: int):
    web3.middleware_onion.add(construct_sign_and_send_raw_middleware(from_account))
   
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    tx_hash = MockERC20.functions.transfer(to, value).transact({"from": from_account.address})

    _ = web3.eth.wait_for_transaction_receipt(tx_hash)

def build_transfer_erc20(web3: Web3, token_address: str, from_address: str, to: str, value: int):
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    web3.eth.sign_transaction
    tx: TxParams = MockERC20.functions.transfer(to, value).build_transaction({"from": from_address})

    return tx["data"]

def get_erc20_balance(web3: Web3, token_address: str, account: str) -> int:
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    return MockERC20.functions.balanceOf(account).call()

def get_env_vars() -> tuple[str, str, str, str, str]:
    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        raise ValueError("RPC_URL is not set")

    user_pk = os.getenv("USER_PRIVATE_KEY")
    if not user_pk:
        raise ValueError("USER_PRIVATE_KEY is not set")

    return rpc_url, user_pk

@click.command()
@click.option('--prompt',
    prompt='Prompt',
    required=True,
    help='Prompt'
)
def run(
    prompt: str
):
    rpc_url, user_pk = get_env_vars()

    print("Prompt: ", prompt)
    print("User private key: ", user_pk)
    print("RPC URL: ", rpc_url)

    client = EthereumClient(URI(rpc_url))
    web3 = client.w3
    
    user: Account = Account.from_key(user_pk)
    agent: Account = generate_agent_account()

    print("User Address: ", user.address)
    print("Agent Address: ", agent.address)
   
    multicall_addr = deploy_multicall(client, user)
    client.multicall = Multicall(client, multicall_addr)

    _ = send_eth(user, agent.address, 1, web3)
    
    safe_addr, safe = deploy_safe_with_create2(client, user, [user.address, agent.address], 1)

    print("Connected to RPC: ", web3.is_connected())

    print("Before ETH Balance: ", get_eth_balance(safe_addr, web3))

    _ = send_eth(user, safe_addr, 1, web3)
    
    print("After ETH Balance: ", get_eth_balance(safe_addr, web3))
   
    info = safe.retrieve_all_info()

    print("Safe Info: ", info)

    random_address = Account.create().address

    token_address = deploy_mock_erc20(web3, user)

    print("Safe ERC20 before transfer: ", get_erc20_balance(web3, token_address, safe_addr))

    transfer_erc20(web3, token_address, user, safe_addr, 100)

    print("Safe ERC20 after transfer: ", get_erc20_balance(web3, token_address, safe_addr))

    multisend = MultiSend(client, address=MULTI_SEND_ADDRESS)

    value = web3.to_wei(0.1, "ether")
    multisend_txs = [
        MultiSendTx(MultiSendOperation.CALL, random_address, value, b"")
        for _ in range(2)
    ] + [
        MultiSendTx(MultiSendOperation.CALL, token_address, 0, build_transfer_erc20(web3, token_address, safe_addr, random_address, 1))
    ]
    safe_multisend_data = multisend.build_tx_data(multisend_txs)

    safe_tx_gas = 600000
    base_gas = 200000

    safe_tx = SafeTx(
        client,
        safe.address,
        multisend.address,
        0,
        safe_multisend_data,
        SafeOperation.DELEGATE_CALL.value,
        safe_tx_gas,
        base_gas,
        client.w3.eth.gas_price,
        None,
        None,
        safe_nonce=safe.retrieve_nonce(),
    )
    safe_tx.sign(agent.key.hex())

    safe_tx.call(tx_sender_address=agent.address)

    tx_hash, _ = safe_tx.execute(
        tx_sender_private_key=agent.key.hex()
    )
    web3.eth.wait_for_transaction_receipt(tx_hash)

    print("Safe ERC20 after multisend: ", get_erc20_balance(web3, token_address, safe_addr))
    print("Random addr ERC20 after multisend: ", get_erc20_balance(web3, token_address, random_address))

    print("After ETH Balance: ", get_eth_balance(random_address, web3))

if __name__ == '__main__':
    run()
