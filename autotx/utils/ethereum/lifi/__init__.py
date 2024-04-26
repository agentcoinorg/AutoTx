import json
import os
from typing import Any
import requests
import re

from autotx.utils.constants import LIFI_API_KEY
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


def add_authorization_info_if_provided(params: dict[str, Any]) -> dict[str, Any] | None:
    headers: dict[str, Any] | None = None
    if LIFI_API_KEY:
        headers = {"x-lifi-api-key": LIFI_API_KEY}
        params["integrator"] = "polywrap"
    return headers


class Lifi:
    BASE_URL = "https://li.quest/v1"

    @classmethod
    def get_quote_to_amount(  # type: ignore
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
        headers = add_authorization_info_if_provided(params)
        attempt_count = 0
        while attempt_count < 2:
            response = requests.post(cls.BASE_URL + "/quote/contractCalls", json=params, headers=headers)
            try:
                return handle_lifi_response(response)
            except LifiApiError as e:
                if (
                    str(e)
                    == "Fetch quote failed with error: Unable to find quote to match expected output."
                    and attempt_count < 1
                ):
                    attempt_count += 1
                    continue
                else:
                    raise e

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
        headers = add_authorization_info_if_provided(params)
        response = requests.get(cls.BASE_URL + "/quote", params=params, headers=headers)  # type: ignore
        return handle_lifi_response(response)
