import json
import logging
import os
import signal
import time
from concurrent.futures import ThreadPoolExecutor
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests
from requests.adapters import HTTPAdapter
#from requests.packages.urllib3.util.retry import Retry DEPRECATED
from urllib3.util import Retry
import websocket
import ssl
import threading
from decimal import Decimal
from datetime import datetime, timedelta
import signal

EXPIRATION_TIME = (datetime.now() + timedelta(days=1)).isoformat()

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

class Record:
    def __init__(self, contract_address, opensea_collection_slug, sudoswap):
        self.ContractAddress = contract_address
        self.OpenseaCollectionSlug = opensea_collection_slug
        self.Sudoswap = sudoswap

def get_collection_slugs():
    ref = db.reference("records")

    records = ref.get()
    print('len(records)', len(records))
    if records is None:
        return []

    slugs = []
    for key in records:
        record = records[key]
        if 'OpenseaCollectionSlug' in record and record['OpenseaCollectionSlug']:
            slugs.append(record['OpenseaCollectionSlug'])

    return slugs


def subscribe(ws, slug):
    subscribe = {
        'topic': f'collection:{slug}',
        'event': 'phx_join',
        'payload': {},
        'ref': 1,
    }
    ws.send(json.dumps(subscribe))

def handle_collection_offer(message):
    data = json.loads(message)
    payload = data['payload']['payload']
    contract_address = payload['asset_contract_criteria']['address']
    # logging.info(f'Received collection offer for {contract_address}')

    ref = db.reference(f"records/{contract_address}")
    record_data = ref.get()

    current_top_bid = Decimal(record_data.get("Opensea", {}).get("topBid", 0.0))
    
    top_bid = Decimal(payload['base_price']) / Decimal(1e18)
    # print('contract_address', contract_address)
    # print('current_top_bid', current_top_bid)
    # print('top_bid', top_bid)

    if current_top_bid < top_bid:
        print('Updating top bid for contract address', contract_address)
        record_data.update({"Opensea": {"bidPayload": payload, "topBid": str(top_bid)}}, expires=json.loads(json.dumps(EXPIRATION_TIME)))
        ref.update(record_data)


def on_message(ws, message):
    data = json.loads(message)
    if data['event'] == 'collection_offer':
        handle_collection_offer(message)

def on_open(ws):
    logging.info('Connected to server')

    if not firebase_admin._apps:
        # Initialize Firebase app
        cred = credentials.Certificate('./credentials.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'
        })

    # Call setup_heartbeat
    print("Setting up heartbeat...")
 
    setup_heartbeat(ws)
    threading.Timer(30, setup_heartbeat, args=[ws]).start()

    # Subscribe to each collection we are monitoring
    collection_slugs = get_collection_slugs()
    print('Retrieved collection slugs', len(collection_slugs))
    for slug in collection_slugs:
        subscribe(ws, slug)
    print('Subscribed to all collections')
   
def on_close(ws, code, reason):
    logging.info('Disconnected from server')
    logging.error(f'Code: {code}, Reason: {reason}', exc_info=True)
    # Attempt to reconnect
    while True:
        try:
            logging.info('Attempting to reconnect...')
            ws.run_forever()
        except Exception as e:
            logging.error(f'Error while reconnecting: {e}')
            time.sleep(5)

def on_error(ws, error):
    logging.error(f"WebSocket error: {error}", exc_info=True)

def setup_heartbeat(socket):
    heartbeat = {
        "topic": "phoenix",
        "event": "heartbeat",
        "payload": {},
        "ref": 0
    }

    heartbeat_string = json.dumps(heartbeat, indent="", separators=(",", ":"))

    logging.info(f"Sending heartbeat {time.strftime('%Y-%m-%d %H:%M:%S')} \n{heartbeat_string}")
    socket.send(heartbeat_string)

def handle_sigint(signal_num, frame):
    logging.info("Received SIGINT signal. Exiting...")
    ws.close()

if __name__ == '__main__':
    # Register signal handler for SIGINT signal
    signal.signal(signal.SIGINT, handle_sigint)
    
    # Create a WebSocket connection
    websocket.enableTrace(False)

    ws = websocket.WebSocketApp(
        'wss://stream.openseabeta.com/socket/websocket?token=28fbebb50f2942b686b48522a76eb9bd',
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()