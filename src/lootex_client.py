import requests
from urllib.parse import urlencode
from config.settings import LOOTEX_API_URL

class LootexClient:
    def __init__(self):
        self.base_url = LOOTEX_API_URL

    def get_nft_events(self, chain_id, contract_address, token_id, platform_type=1, limit=30, page=1):
        endpoint = f"{self.base_url}/orders/history"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "limit": limit,
            "chainId": chain_id,
            "contractAddress": contract_address,
            "tokenId": token_id,
            "page": page,
            "platformType": platform_type
        }
        
        url = f"{endpoint}?{urlencode(params)}"
        # print(f"Requesting URL: {url}")
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None