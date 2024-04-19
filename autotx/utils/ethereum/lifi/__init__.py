from decimal import Decimal
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
    def get_quote(
        cls,
        from_token: ETHAddress,
        to_token: ETHAddress,
        amount: int,
        _from: ETHAddress,
        chain: ChainId,
        slippage: float
    ) -> dict[str, Any]:
        params = {
            "fromToken": from_token.hex,
            "toToken": to_token.hex,
            "fromAmount": amount,
            "fromAddress": _from.hex,
            "fromChain": chain.value,
            "toChain": chain.value,
            "slippage": slippage
        }
        response = requests.get(cls.BASE_URL + "/quote", params=params) # type: ignore
        response_json: dict[str, Any] = json.loads(response.text)

        if response.status_code == 200:
            return response_json

        if response.status_code == 429 or (response_json["message"] == "Unauthorized" and response_json["code"] == 1005):
            raise LifiApiError("Rate limit exceeded")

        raise LifiApiError(f"Fetch quote failed with error: {response_json['message']}")

    @classmethod
    def get_token_price(cls, address: ETHAddress, chain: ChainId) -> Decimal:
        params = {"chain": chain.value, "token": address.hex}
        response = requests.get(cls.BASE_URL + "/token", params=params)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            price = response_json.get("priceUSD")
            if price == None:
                raise LifiApiError(
                    f"No price available from token: {response_json['symbol']}"
                )

            return Decimal(price)

        raise LifiApiError("Error fetching price")
