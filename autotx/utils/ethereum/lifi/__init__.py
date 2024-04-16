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
    ) -> dict[str, Any]:
        params = {
            "fromToken": from_token.hex,
            "toToken": to_token.hex,
            "fromAmount": amount,
            "fromAddress": _from,
            "fromChain": chain.value,
            "toChain": chain.value,
        }
        response = requests.get(cls.BASE_URL + "/quote", params=params)
        if response.status_code == 200:
            return json.loads(response.text)

        raise Exception("Error fetching quote")

    @classmethod
    def get_token_price(cls, address: ETHAddress, chain: ChainId) -> float:
        params = {"chain": chain.value, "token": address.hex}
        print(params)
        response = requests.get(cls.BASE_URL + "/token", params=params)
        if response.status_code == 200:
            token_information = json.loads(response.text)
            price = token_information.get("priceUSD")
            if price == None:
                raise Exception(
                    f"Couldn't fetch price for token with address: {address.hex}"
                )

            return float(price)

        raise Exception("Error fetching price")
