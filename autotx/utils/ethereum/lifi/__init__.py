import json
from typing import Any
import requests

from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.networks import ChainId


class LifiApiError(Exception):
    pass


class Lifi:
    BASE_URL = "https://li.quest/v1"

    @classmethod
    def get_quote_to_amount(
        cls,
        from_token: ETHAddress,
        to_token: ETHAddress,
        amount: int,
        _from: ETHAddress,
        chain: ChainId,
        slippage: float,
    ):
        params = {
            "fromToken": from_token.hex,
            "toToken": to_token.hex,
            "toAmount": str(amount),
            "fromAddress": _from.hex,
            "fromChain": chain.value,
            "toChain": chain.value,
            "slippage": slippage,
            "contractCalls": []
        }
        response = requests.post(cls.BASE_URL + "/quote/contractCalls", json=params)  # type: ignore
        response_json: dict[str, Any] = json.loads(response.text)
        if response.status_code == 200:
            return response_json

        if response.status_code == 429 or (
            response_json["message"] == "Unauthorized" and response_json["code"] == 1005
        ):
            raise LifiApiError("Rate limit exceeded")

        raise LifiApiError(f"Fetch quote failed with error: {response_json['message']}")

    @classmethod
    def get_quote_from_amount(
        cls,
        from_token: ETHAddress,
        to_token: ETHAddress,
        amount: int,
        _from: ETHAddress,
        chain: ChainId,
        slippage: float,
    ) -> dict[str, Any]:
        params = {
            "fromToken": from_token.hex,
            "toToken": to_token.hex,
            "fromAmount": amount,
            "fromAddress": _from.hex,
            "fromChain": chain.value,
            "toChain": chain.value,
            "slippage": slippage,
        }
        response = requests.get(cls.BASE_URL + "/quote", params=params)  # type: ignore
        response_json: dict[str, Any] = json.loads(response.text)

        if response.status_code == 200:
            return response_json

        if response.status_code == 429 or (
            response_json["message"] == "Unauthorized" and response_json["code"] == 1005
        ):
            raise LifiApiError("Rate limit exceeded")

        raise LifiApiError(f"Fetch quote failed with error: {response_json['message']}")
