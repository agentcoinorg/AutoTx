import json
from langchain.tools import tool

class BridgeTools:
    @tool("Get quote of bridge transfer transaction")
    def get_quote(payload):
        """
        :param payload: str, a string representation of a quote object

        example payload:
        {
            fromChain: str, The sending chain. Can be the chain id or chain key
            toChain: str, The receiving chain. Can be the chain id or chain key
            fromToken: str, The token that should be transferred. Must be the symbol
            toToken: str, The token that should be transferred to. Must be the symbol
            fromAmount: str, The amount that should be sent including all decimals
        }

        :result transaction_request: str, stringified representation of ethereun transaction object
        """

        transaction_request = {
            "to": "0xCOOL_ADDRESS",
            "data": "0xCOOL_DATA",
            "value": "0",
        }
        return json.dumps(transaction_request)

