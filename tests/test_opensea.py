import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.opensea_client import OpenSeaClient

def get_user_input():
    if len(sys.argv) == 4:
        return sys.argv[1], sys.argv[2], sys.argv[3]
    else:
        chain = input("Enter the chain (e.g., matic): ")
        contract_address = input("Enter the contract address: ")
        token_id = input("Enter the token ID: ")
        return chain, contract_address, token_id

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
    return {
        'event_type': 'sale',
        'created_time': datetime.fromtimestamp(event['event_timestamp']).isoformat(),
        'from_address': event['seller'],
        'to_address': event['buyer'],
        'txhash': event['transaction'],
        'collection_name': event['nft']['collection'],
        'contract_address': event['nft']['contract'],
        'token_id': event['nft']['identifier'],
        'quantity': event['quantity']
    }

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

def get_opensea_listing_events(chain, contract_address, token_id):
    client = OpenSeaClient()
    events = client.get_nft_events(chain=chain, contract_address=contract_address, token_id=token_id, event_types=["listing"])
    return [format_listing_event(event) for event in events.get('asset_events', []) if event['event_type'] == 'order']

def get_opensea_sale_events(chain, contract_address, token_id):
    client = OpenSeaClient()
    events = client.get_nft_events(chain=chain, contract_address=contract_address, token_id=token_id, event_types="sale")
    return [format_sale_event(event) for event in events.get('asset_events', [])]

def get_opensea_cancel_events(chain, contract_address, token_id):
    client = OpenSeaClient()
    events = client.get_nft_events(chain=chain, contract_address=contract_address, token_id=token_id, event_types="cancel")
    return [event for event in (format_cancel_event(event) for event in events.get('asset_events', [])) if event is not None]

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
    chain, contract_address, token_id = get_user_input()
    print(f"\nFetching events for: Chain: {chain}, Contract: {contract_address}, Token ID: {token_id}")
    
    listing_events = get_opensea_listing_events(chain, contract_address, token_id)
    cancel_events = get_opensea_cancel_events(chain, contract_address, token_id)
    sale_events = get_opensea_sale_events(chain, contract_address, token_id)
    
    print_events(listing_events, "listing")
    print_events(cancel_events, "cancel")
    print_events(sale_events, "sale")