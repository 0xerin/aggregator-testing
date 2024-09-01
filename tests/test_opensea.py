import sys
import os
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.opensea_client import OpenSeaClient

def get_user_input():
    chain = input("Enter the chain (e.g., matic): ")
    contract_address = input("Enter the contract address: ")
    token_id = input("Enter the token ID: ")
    start_time = input("Enter start time (YYYY-MM-DD HH:MM:SS) or press Enter for no start time: ")
    end_time = input("Enter end time (YYYY-MM-DD HH:MM:SS) or press Enter for no end time: ")
    return chain, contract_address, token_id, start_time, end_time

def parse_input_time(time_str):
    if not time_str:
        return None
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return int(dt.replace(tzinfo=timezone.utc).timestamp())
    except ValueError:
        print(f"Invalid time format: {time_str}. Please use YYYY-MM-DD HH:MM:SS.")
        return None

def format_listing_event(event):
    quantity = event['quantity']
    total_price = float(event['payment']['quantity']) / (10 ** event['payment']['decimals'])
    price_per_token = total_price / quantity

    return {
        'event_type': 'listing',
        'created_time': datetime.fromtimestamp(event['start_date']).isoformat(),
        'expiration_time': datetime.fromtimestamp(event['expiration_date']).isoformat(),
        'owner_address': event['maker'],
        'price': f"{price_per_token:.6f} {event['payment']['symbol']}",
        'txhash': event['order_hash'],
        'collection_name': event['asset']['collection'],
        'contract_address': event['asset']['contract'],
        'token_id': event['asset']['identifier'],
        'quantity': event['quantity']
    }

def format_sale_event(event):
    try:
        formatted_event = {
            'event_type': 'sale',
            'created_time': datetime.fromtimestamp(event.get('event_timestamp', 0)).isoformat(),
            'from_address': event.get('from_address', 'N/A'),
            'to_address': event.get('to_address', 'N/A'),
            'txhash': event.get('transaction', 'N/A'),
            'collection_name': event.get('nft', {}).get('collection', 'N/A'),
            'contract_address': event.get('nft', {}).get('contract', 'N/A'),
            'token_id': event.get('nft', {}).get('identifier', 'N/A'),
            'quantity': event.get('quantity', 0)
        }
        
        required_fields = ['created_time', 'from_address', 'to_address', 'txhash', 'contract_address', 'token_id']
        if all(formatted_event.get(field) != 'N/A' for field in required_fields):
            return formatted_event
        else:
            print(f"Warning: Incomplete sale event data: {event}")
            return None
    except Exception as e:
        print(f"Error formatting sale event: {e}")
        return None
    
def format_cancel_event(event):
    if event.get('order_type') == 'offer':
        return None
    return {
        'event_type': 'cancel',
        'created_time': datetime.fromtimestamp(event['event_timestamp']).isoformat(),
        'txhash': event['order_hash'],
        'collection_name': event['nft']['collection'],
        'contract_address': event['nft']['contract'],
        'token_id': event['nft']['identifier']
    }

def get_opensea_events(chain, contract_address, token_id, event_types, after=None, before=None):
    client = OpenSeaClient()
    events = client.get_nft_events(chain=chain, contract_address=contract_address, token_id=token_id, 
                                   event_types=event_types, after=after, before=before)
    return events.get('asset_events', [])

def get_opensea_listing_events(chain, contract_address, token_id, start_time_str=None, end_time_str=None):
    after = parse_input_time(start_time_str)
    before = parse_input_time(end_time_str)
    events = get_opensea_events(chain, contract_address, token_id, ["listing"], after, before)
    return [format_listing_event(event) for event in events if event['event_type'] == 'order']

def get_opensea_sale_events(chain, contract_address, token_id, start_time_str=None, end_time_str=None):
    after = parse_input_time(start_time_str)
    before = parse_input_time(end_time_str)
    events = get_opensea_events(chain, contract_address, token_id, "transfer", after, before)
    return [event for event in (format_sale_event(event) for event in events) if event is not None]

def get_opensea_cancel_events(chain, contract_address, token_id, start_time_str=None, end_time_str=None):
    after = parse_input_time(start_time_str)
    before = parse_input_time(end_time_str)
    events = get_opensea_events(chain, contract_address, token_id, "cancel", after, before)
    return [event for event in (format_cancel_event(event) for event in events) if event is not None]

def print_events(events, event_type):
    print(f"\n--- {event_type.capitalize()} Events ---")
    if events:
        valid_events = [event for event in events if event is not None]
        print(f"Total {event_type} events: {len(valid_events)}")
        for event in valid_events:
            print(json.dumps(event, indent=2))
            print()
    else:
        print(f"No {event_type} events found.")

if __name__ == "__main__":
    chain, contract_address, token_id, start_time_str, end_time_str = get_user_input()
    print(f"\nFetching events for: Chain: {chain}, Contract: {contract_address}, Token ID: {token_id}")

    after = parse_input_time(start_time_str)
    before = parse_input_time(end_time_str)

    listing_events = get_opensea_listing_events(chain, contract_address, token_id, after, before)
    cancel_events = get_opensea_cancel_events(chain, contract_address, token_id, after, before)
    sale_events = get_opensea_sale_events(chain, contract_address, token_id, after, before)
    
    print_events(listing_events, "listing")
    print_events(cancel_events, "cancel")
    print_events(sale_events, "sale")