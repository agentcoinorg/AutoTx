from langchain.tools import tool
from web3 import Web3

# from utils.ethereum import provider


class EthereumTools:
    @tool("Get balance from ethereum address")
    def get_balance(address):
        """
        Allows to get the balance of a given address in Ethereum Blockchain
        """
        # w3 = Web3(provider=provider)
        return "123"

    @tool("Send transaction to ethereum blockchain")
    def send_transaction(payload):
        """
        :param payload: str, a string representation of a ethereum transaction containing the following keys:

        data: Optional[str], the calldata of the transaction
        to: str, the address to whom the transaction is going to be sent
        value: int, number of ether (in wei) to transfer

        example payload:
        {
            "data": 0xENCODED_TRANSACTION_DATA
            "to": 0xETHEREUM_ADDRESS
            "value": 0
        }

        :result hash: str, the hash of the transaction sent
        """
        return "0xhash"
