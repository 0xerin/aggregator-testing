import sys
import os
import json
from datetime import datetime, timedelta, timezone


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_lootex import (
    get_lootex_listing_events,
    get_lootex_cancel_events,
    get_lootex_sale_events
)
from tests.test_opensea import (
    get_opensea_listing_events,
    get_opensea_cancel_events,
    get_opensea_sale_events
)

# Chain ID mapping
CHAIN_ID_MAP = {
    "137": "matic",
    "matic": "137",
    "1": "ethereum",
    "ethereum": "1",
    "8453": "base",
    "base": "8453"
}

def get_chain_info(chain_input):
    chain_input = str(chain_input).lower()
    if chain_input in CHAIN_ID_MAP:
        chain_id = CHAIN_ID_MAP[chain_input] if chain_input.isalpha() else chain_input
        opensea_chain = CHAIN_ID_MAP[chain_id]
    else:
        chain_id = chain_input
        opensea_chain = chain_input
    return chain_id, opensea_chain

def compare_events(lootex_events, opensea_events, event_type):
    print(f"\n--- Comparing {event_type.capitalize()} Events ---")
    
    lootex_dict = {event['txhash']: event for event in lootex_events}
    opensea_dict = {event['txhash']: event for event in opensea_events}
    
    matching_events = set(lootex_dict.keys()) & set(opensea_dict.keys())
    lootex_only = set(lootex_dict.keys()) - set(opensea_dict.keys())
    opensea_only = set(opensea_dict.keys()) - set(lootex_dict.keys())
    
    print(f"Total matching events: {len(matching_events)}")
    print(f"Events only in Lootex: {len(lootex_only)}")
    print(f"Events only in OpenSea: {len(opensea_only)}")
    
    if lootex_only:
        print("\nEvents only in Lootex:")
        for txhash in lootex_only:
            print(f"Transaction Hash: {txhash}")
            # print(json.dumps(lootex_dict[txhash], indent=2))
    
    if opensea_only:
        print("\nEvents only in OpenSea:")
        for txhash in opensea_only:
            print(f"Transaction Hash: {txhash}")
            # print(json.dumps(opensea_dict[txhash], indent=2))

def main():
    chain_input = input("Enter the chain ID or name (e.g., 137, matic, 8453, base): ")
    contract_address = input("Enter the contract address: ")
    token_id = input("Enter the token ID: ")

    chain_id, opensea_chain = get_chain_info(chain_input)

    event_types = ['listing', 'cancel', 'sale']
    
    for event_type in event_types:
        lootex_events = globals()[f'get_lootex_{event_type}_events'](chain_id, contract_address, token_id)
        opensea_events = globals()[f'get_opensea_{event_type}_events'](opensea_chain, contract_address, token_id)
        compare_events(lootex_events, opensea_events, event_type)

if __name__ == "__main__":
    main()