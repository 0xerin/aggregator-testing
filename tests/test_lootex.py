import sys
import os
import json
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lootex_client import LootexClient

def get_user_input():
    chain_id = input("Enter the chain ID (e.g., 137 for Polygon): ")
    contract_address = input("Enter the contract address: ")
    token_id = input("Enter the token ID: ")
    start_time = input("Enter start time (YYYY-MM-DD HH:MM:SS) or press Enter for no start time: ")
    end_time = input("Enter end time (YYYY-MM-DD HH:MM:SS) or press Enter for no end time: ")
    return chain_id, contract_address, token_id, start_time, end_time

def parse_input_time(time_str):
    if not time_str:
        return None
    try:
        local_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return local_time.replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Invalid time format: {time_str}. Please use YYYY-MM-DD HH:MM:SS.")
        return None

def test_lootex_events_with_time_range():
    client = LootexClient()
    chain_id, contract_address, token_id, start_time_str, end_time_str = get_user_input()

    start_time = parse_input_time(start_time_str)
    end_time = parse_input_time(end_time_str)

    if start_time is None or end_time is None:
        filtered_events = client.get_nft_events(chain_id, contract_address, token_id)
    else:
        filtered_events = client.get_filtered_events(chain_id, contract_address, token_id, start_time, end_time)

    if not filtered_events:
        print("No events found in the specified time range")
        return
    
    # for event in filtered_events:
    #         event_time = client.parse_event_time(event)
    #         assert start_time <= event_time <= end_time, f"Event time {event_time} is outside the specified range"

    listing_events = [format_listing_event(e) for e in filtered_events if e['category'] == 'list']
    cancel_events = [format_cancel_event(e) for e in filtered_events if e['category'] == 'cancel']
    sale_events = [format_sale_event(e) for e in filtered_events if e['category'] == 'sale']

    print_events(listing_events, "listing")
    print_events(cancel_events, "cancel")
    print_events(sale_events, "sale")



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

def get_lootex_listing_events(chain_id, contract_address, token_id, start_time=None, end_time=None):
    client = LootexClient()
    events = client.get_filtered_events(chain_id, contract_address, token_id, start_time, end_time)
    return [format_listing_event(event) for event in events if event['category'] == 'list']

def get_lootex_cancel_events(chain_id, contract_address, token_id, start_time=None, end_time=None):
    client = LootexClient()
    events = client.get_filtered_events(chain_id, contract_address, token_id, start_time, end_time)
    return [format_cancel_event(event) for event in events if event['category'] == 'cancel']

def get_lootex_sale_events(chain_id, contract_address, token_id, start_time=None, end_time=None):
    client = LootexClient()
    events = client.get_filtered_events(chain_id, contract_address, token_id, start_time, end_time)
    return [format_sale_event(event) for event in events if event['category'] == 'sale']
def print_events(events, event_type):
    print(f"\n--- {event_type.capitalize()} Events ---")
    print(f"Total {event_type} events: {len(events)}")
    for event in events:
        print(json.dumps(event, indent=2))
        print()

if __name__ == "__main__":
    test_lootex_events_with_time_range()
    # chain_id, contract_address, token_id = get_user_input()
    # print(f"\nFetching events for: Chain ID: {chain_id}, Contract: {contract_address}, Token ID: {token_id}")
    
    # all_events = get_lootex_events(chain_id, contract_address, token_id)
    # print(f"Total events: {len(all_events)}")

    # for event in all_events:
    #     print(f"Event type: {event.get('category')}, Hash: {event.get('hash')}")

    # listing_events = get_lootex_listing_events(chain_id, contract_address, token_id)
    # cancel_events = get_lootex_cancel_events(chain_id, contract_address, token_id)
    # sale_events = get_lootex_sale_events(chain_id, contract_address, token_id)
    
    # print_events(listing_events, "listing")
    # print_events(cancel_events, "cancel")
    # print_events(sale_events, "sale")