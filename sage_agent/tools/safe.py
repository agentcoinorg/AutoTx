from langchain.tools import tool


"""
:param payload: str, a string representation of a safe transaction with signatures

example payload:
{
    "data": {
        to: str
        value: str
        data: str
        operation: 1 | 2
        safeTxGas: str
        baseGas: str
        gasPrice: str
        gasToken: str
        refundReceiver: str
        nonce: int
    },
    "signatures": {
        [address: str]: str
    }
}
"""
class SafeTools:
    # @tool("Create multisend")
    # def create_multisend():
    #     pass

    @tool("Create transaction")
    def create_transaction(payload):
        """
        :param payload: str, a string representation of a ethereum transaction

        example payload:
        {
            to: str
            value: str
            data: str
        }

        :return safe_transaction_hash: str, hash of the recently created safe transaction
        """
        
        print(payload)
        return "0xSAFE_TRANSACTION_HASH"

    @tool("Execute signed transaction in safe")
    def execute_transaction(safe_transaction_hash):
        """
        :param safe_transaction_hash: str, hash of the transaction to be signed

        :return hash: str, hash of transaction executed
        """
        return "0xEXECUTED_TRANSACTION_HASH"

    @tool("Sign transaction")
    def sign_transaction(hash):
        """
        :param hash: str, transaction hash to add signature

        :return signature: str, signature added to transaction from hash given
        """
        return "0xSIGNATURE"

    # @tool("Deploy")
    # def deploy():
    #     pass
