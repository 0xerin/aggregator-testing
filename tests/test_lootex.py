import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lootex_client import LootexClient

def get_user_input():
    chain_id = input("Enter the chain ID (e.g., 137 for Polygon): ")
    contract_address = input("Enter the contract address: ")
    token_id = input("Enter the token ID: ")
    return chain_id, contract_address, token_id

def standardize_timestamp(timestamp_str):
    if timestamp_str and timestamp_str != 'N/A':
        dt = datetime.fromisoformat(timestamp_str.replace('Z', ''))
        adjusted_dt = dt + timedelta(hours=8)
        return adjusted_dt.strftime('%Y-%m-%dT%H:%M:%S')
    return 'N/A'

def format_listing_event(event):
    return {
        'event_type': 'listing',
        'created_time': standardize_timestamp(event.get('startTime', 'N/A')),
        'expiration_time': standardize_timestamp(event.get('endTime', 'N/A')),
        'owner_address': event.get('fromAddress', 'N/A'),
        'price': f"{event.get('price', 'N/A')} {event.get('currencySymbol', 'N/A')}",
        'txhash': event.get('hash', 'N/A'),
        'collection_name': event.get('collectionName', 'N/A').lower().replace(' ', '-'),
        'contract_address': event.get('contractAddress', 'N/A'),
        'token_id': event.get('tokenId', 'N/A'),
        'quantity': int(event.get('amount', 0))
    }

def format_cancel_event(event):
    return {
        'event_type': 'cancel',
        'created_time': standardize_timestamp(event.get('startTime', 'N/A')),
        'txhash': event.get('hash', 'N/A'),
        'collection_name': event.get('collectionName', 'N/A').lower().replace(' ', '-'),
        'contract_address': event.get('contractAddress', 'N/A'),
        'token_id': event.get('tokenId', 'N/A')
    }

def format_sale_event(event):
    return {
        'event_type': 'sale',
        'created_time': standardize_timestamp(event.get('startTime', 'N/A')),
        'from_address': event.get('fromAddress', 'N/A'),
        'to_address': event.get('toAddress', 'N/A'),
        'txhash': event.get('txHash', 'N/A'),
        'collection_name': event.get('collectionName', 'N/A').lower().replace(' ', '-'),
        'contract_address': event.get('contractAddress', 'N/A'),
        'token_id': event.get('tokenId', 'N/A'),
        'quantity': int(event.get('amount', 0))
    }

def get_lootex_events(chain_id, contract_address, token_id, limit=30):
    client = LootexClient()
    all_events = []
    page = 1
    while True:
        response = client.get_nft_events(chain_id, contract_address, token_id, limit=limit, page=page)
        if response and 'ordersHistory' in response:
            events = response['ordersHistory']
            all_events.extend(events)
            if len(events) < limit:
                break
            page += 1
        else:
            break
    # print("Raw API response:")
    # print(json.dumps(response, indent=2))
    return all_events

def get_lootex_listing_events(chain_id, contract_address, token_id):
    events = get_lootex_events(chain_id, contract_address, token_id)
    return [format_listing_event(event) for event in events if event['category'] == 'list']

def get_lootex_cancel_events(chain_id, contract_address, token_id):
    events = get_lootex_events(chain_id, contract_address, token_id)
    return [format_cancel_event(event) for event in events if event['category'] == 'cancel']

def get_lootex_sale_events(chain_id, contract_address, token_id):
    events = get_lootex_events(chain_id, contract_address, token_id)
    return [format_sale_event(event) for event in events if event['category'] == 'sale']

def print_events(events, event_type):
    print(f"\n--- {event_type.capitalize()} Events ---")
    print(f"Total {event_type} events: {len(events)}")
    for event in events:
        print(json.dumps(event, indent=2))
        print()

if __name__ == "__main__":
    chain_id, contract_address, token_id = get_user_input()
    print(f"\nFetching events for: Chain ID: {chain_id}, Contract: {contract_address}, Token ID: {token_id}")
    
    all_events = get_lootex_events(chain_id, contract_address, token_id)
    print(f"Total events: {len(all_events)}")

    for event in all_events:
        print(f"Event type: {event.get('category')}, Hash: {event.get('hash')}")

    listing_events = get_lootex_listing_events(chain_id, contract_address, token_id)
    cancel_events = get_lootex_cancel_events(chain_id, contract_address, token_id)
    sale_events = get_lootex_sale_events(chain_id, contract_address, token_id)
    
    print_events(listing_events, "listing")
    print_events(cancel_events, "cancel")
    print_events(sale_events, "sale")