import json
from typing import Any
import requests
import re

from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.networks import ChainId


class LifiApiError(Exception):
    pass


class TokenNotSupported(LifiApiError):
    def __init__(self, token_address: str):
        super().__init__(token_address)
        self.token_address = token_address


def handle_lifi_response(response: requests.Response) -> dict[str, Any]:
    response_json: dict[str, Any] = json.loads(response.text)
    if response.status_code == 200:
        return response_json

    if response_json["code"] == 1011:
        match = re.search(r"0x[a-fA-F0-9]+", response_json["message"])
        if match:
            token_address = match.group()
            raise TokenNotSupported(token_address)

    if response.status_code == 429 or (
        response_json["message"] == "Unauthorized" and response_json["code"] == 1005
    ):
        raise LifiApiError("Rate limit exceeded")

    raise LifiApiError(f"Fetch quote failed with error: {response_json['message']}")


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
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "fromToken": from_token.hex,
            "toToken": to_token.hex,
            "toAmount": str(amount),
            "fromAddress": _from.hex,
            "fromChain": chain.value,
            "toChain": chain.value,
            "slippage": slippage,
            "contractCalls": [],
        }
        response = requests.post(cls.BASE_URL + "/quote/contractCalls", json=params)
        return handle_lifi_response(response)

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
        return handle_lifi_response(response)
