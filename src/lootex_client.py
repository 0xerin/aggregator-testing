import requests
from urllib.parse import urlencode
from config.settings import LOOTEX_API_URL
from datetime import datetime, timezone

class LootexClient:
    def __init__(self):
        self.base_url = LOOTEX_API_URL

    def get_nft_events(self, chain_id, contract_address, token_id, limit=30, page=1, start_time=None, end_time=None):
        endpoint = f"{self.base_url}/orders/history"
        headers = {
            "Content-Type": "application/json"
        }
        
        all_events = []
        page = 1
        
        while True:
            params = {
                "limit": limit,
                "chainId": chain_id,
                "contractAddress": contract_address,
                "tokenId": token_id,
                "page": page,
                "platformType": 1
            }
            
            if start_time:
                params["startTimeGt"] = start_time.isoformat() + "Z"
            if end_time:
                params["startTimeLt"] = end_time.isoformat() + "Z"

            url = f"{endpoint}?{urlencode(params)}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('ordersHistory', [])
                all_events.extend(events)
                
                pagination = data.get('pagination', {})
                total_pages = pagination.get('totalPage', 1)
                
                if page >= total_pages or len(events) < limit:
                    break
                
                page += 1
            else:
                print(f"Error on page {page}: {response.status_code}")
                print(response.text)
                break

        return all_events
        
    def get_filtered_events(self, chain_id, contract_address, token_id, start_time, end_time, limit=30):
        return self.get_nft_events(chain_id, contract_address, token_id, limit, start_time=start_time, end_time=end_time)
  
        if start_time is None and end_time is None:
            return all_events
    
        filtered_events = [
            event for event in all_events 
            if start_time <= self.parse_event_time(event) <= end_time
        ]
        
        return filtered_events