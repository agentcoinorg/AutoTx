import json
import os

import requests


class CoingeckoApi:
    BASE_URL: str = "https://api.coingecko.com/api/v3"
    API_KEY = os.getenv("COINGECKO_API_KEY")

    def request(self, endpoint: str):
        headers = {"x-cg-demo-api-key": self.API_KEY}
        response = requests.get(self.BASE_URL + endpoint, headers=headers)
        return json.loads(response.text)
