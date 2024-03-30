import os

import requests


class CoingeckoApi:
    BASE_URL: str = "https://api.coingecko.com/api/v3"
    API_KEY = os.getenv("COINGECKO_API_KEY")

    def request(self, endpoint: str):
        if self.API_KEY == None:
            raise "You must add a value to COINGECKO_API_KEY key in .env file"

        headers = {"x-cg-demo-api-key": self.API_KEY}
        response = requests.get(self.BASE_URL.join(endpoint), headers=headers)

        return response.text

    def chain_id_to_platform(self):
        pass
