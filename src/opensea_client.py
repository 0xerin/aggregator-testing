import requests
from config.settings import OPENSEA_API_KEY, OPENSEA_API_URL

class OpenSeaClient:
    def __init__(self):
        self.api_key = OPENSEA_API_KEY
        self.base_url = OPENSEA_API_URL
    
    def get_nft_events(self, chain, contract_address, token_id, event_types=None, after=None, before=None, limit=50):
        url = f"{self.base_url}/events/chain/{chain}/contract/{contract_address}/nfts/{token_id}"
        headers = {"accept": "application/json", "X-API-KEY": self.api_key}
        params = {"limit": limit}

        if event_types:
            if isinstance(event_types, str):
                params["event_type"] = event_types
        elif isinstance(event_types, list):
            params["event_type"] = ",".join(event_types)
        
        if after is not None:
            params["after"] = int(after)
        if before is not None:
            params["before"] = int(before)
            
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None