from decimal import Decimal
import json
from typing import Any
import requests

from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.networks import ChainId


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
        if response.status_code == 200:
            quote: dict[str, Any] = json.loads(response.text)
            return quote

        raise Exception("Error fetching quote")

    @classmethod
    def get_token_price(cls, address: ETHAddress, chain: ChainId) -> Decimal:
        params = {"chain": chain.value, "token": address.hex}
        response = requests.get(cls.BASE_URL + "/token", params=params)
        if response.status_code == 200:
            price = json.loads(response.text).get("priceUSD")
            if price == None:
                raise Exception(
                    f"Couldn't fetch price for token with address: {address.hex}"
                )

            return Decimal(price)

        raise Exception("Error fetching price")
