import random
from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress, HexStr
from gnosis.eth import EthereumClient
from gnosis.safe import ProxyFactory
from gnosis.safe.safe_create2_tx import SafeCreate2TxBuilder
from hexbytes import HexBytes
from web3 import Web3
from web3.types import Wei

from .send_tx import send_tx
from .constants import GAS_PRICE_MULTIPLIER, MASTER_COPY_ADDRESS, PROXY_FACTORY_ADDRESS

def deploy_safe_with_create2(client: EthereumClient, account: LocalAccount, signers: list[str], threshold: int) -> ChecksumAddress:
    w3 = client.w3

    salt_nonce = generate_salt_nonce()

    builder = SafeCreate2TxBuilder(
        w3=w3,
        master_copy_address=MASTER_COPY_ADDRESS,
        proxy_factory_address=PROXY_FACTORY_ADDRESS,
    )
    
    setup_data = builder._get_initial_setup_safe_data(
        owners=signers,
        threshold=threshold,
    )
    safe_address: ChecksumAddress = builder.calculate_create2_address(setup_data, salt_nonce)

    # Check if safe is already deployed
    if w3.eth.get_code(safe_address) != w3.to_bytes(hexstr=HexStr("0x")):
        print("Safe already deployed", safe_address)
        return safe_address
    
    safe_creation_tx = builder.build(
        owners=signers,
        threshold=threshold,
        salt_nonce=salt_nonce,
        gas_price=0,
    )
    
    if safe_address != safe_creation_tx.safe_address:
        raise ValueError("Create2 address mismatch")

    send_tx(
        w3,
        {
            "to": safe_creation_tx.safe_address,
            "value": safe_creation_tx.payment,
            "gasPrice": Wei(int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER))
        },
        account=account,
    )

    proxy_factory = ProxyFactory(Web3.to_checksum_address(PROXY_FACTORY_ADDRESS), client)

    ethereum_tx_sent = proxy_factory.deploy_proxy_contract_with_nonce(
        account,
        Web3.to_checksum_address(MASTER_COPY_ADDRESS),
        safe_creation_tx.safe_setup_data,
        salt_nonce,
        safe_creation_tx.gas,
        int(w3.eth.gas_price * GAS_PRICE_MULTIPLIER),
    )

    print("Deploying safe address: ", safe_address, ", tx: ", ethereum_tx_sent.tx_hash.hex())
    tx_receipt = w3.eth.wait_for_transaction_receipt(HexBytes(ethereum_tx_sent.tx_hash))
    if tx_receipt["status"] != 1:
        raise ValueError("Transaction failed")

    return safe_address

def generate_salt_nonce() -> int:
    return random.getrandbits(256) - 1

