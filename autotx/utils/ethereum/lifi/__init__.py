import asyncio
from typing import Any
import re
import aiohttp

from autotx.utils import http_requests
from autotx.utils.constants import LIFI_API_KEY
from autotx.eth_address import ETHAddress
from autotx.utils.ethereum.networks import ChainId


class LifiApiError(Exception):
    pass


class TokenNotSupported(LifiApiError):
    def __init__(self, token_address: str):
        super().__init__(token_address)
        self.token_address = token_address


async def handle_lifi_response(response: aiohttp.ClientResponse) -> dict[str, Any]:
    response_json: dict[str, Any] = await response.json()
    if response.status == 200:
        return response_json

    if response_json["code"] == 1011:
        match = re.search(r"0x[a-fA-F0-9]+", response_json["message"])
        if match:
            token_address = match.group()
            raise TokenNotSupported(token_address)

    if response.status == 429 or (
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
    async def get_quote_to_amount(
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
        while True:
            try:
                return await handle_lifi_response(await http_requests.post(cls.BASE_URL + "/quote/contractCalls", json=params, headers=headers))
            except LifiApiError as e:
                if "No available quotes for the requested transfer" in str(e) or "Unable to find quote to match expected output" in str(e):
                    if attempt_count < 5:
                        attempt_count += 1
                        await asyncio.sleep(1)                   
                        continue
                raise e

    @classmethod
    async def get_quote_from_amount(
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

        attempt_count = 0
        while True:
            try:
                return await handle_lifi_response( await http_requests.get(cls.BASE_URL + "/quote", params=params, headers=headers))
            except LifiApiError as e:
                if "No available quotes for the requested transfer" in str(e) or "Unable to find quote to match expected output" in str(e):
                    if attempt_count < 5:
                        attempt_count += 1
                        await asyncio.sleep(1)                   
                        continue
                raise e