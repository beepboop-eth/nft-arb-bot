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
from requests.packages.urllib3.util.retry import Retry
import websocket
import ssl


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

def initialize_database():
    cred = credentials.Certificate('./credentials.json')
    app = firebase_admin.initialize_app(cred, name='my-app', options={
        'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/',
    })
    return db.reference('records', app=app)

class Record:
    def __init__(self, contract_address, opensea_collection_slug, sudoswap):
        self.ContractAddress = contract_address
        self.OpenseaCollectionSlug = opensea_collection_slug
        self.Sudoswap = sudoswap

def get_collection_slugs(ref):
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

def handle_collection_offer(message, db, rate_limiter):
    data = json.loads(message)
    payload = data['payload']['payload']
    contract_address = payload['asset_contract_criteria']['address']
    logging.info(f'Handling collection offer for {contract_address}')
    ref = db.child(f'records/{contract_address}')
    ref.set(Record(contract_address, payload['collection']['slug'], payload))

def on_message(ws, message):
    handle_collection_offer(message, db, rate_limiter)

def on_open(ws):
    logging.info('Connected to server')

    # Call setup_heartbeat
    print("Setting up heartbeat...")
    setup_heartbeat(ws)

    # Subscribe to each collection we are monitoring
    # collection_slugs = get_collection_slugs(db)
    # print('Retreived collection slugs', len(collection_slugs))
    # for slug in collection_slugs:
    #     subscribe(ws, slug)
    #     print(f'Subscribed to {slug}')

   
def on_close(ws):
    logging.info('Disconnected from server')
    # Attempt to reconnect
    while True:
        try:
            logging.info('Attempting to reconnect...')
            ws.run_forever()
        except Exception as e:
            logging.error(f'Error while reconnecting: {e}')
            time.sleep(5)

def on_error(ws, error):
    logging.error(f'WebSocket error: {error}')

def run():
    while True:
        try:
            # Initialize Firebase database
            db = None
            if db is None: 
              db = initialize_database()

            # Create a rate limiter to limit the number of requests we send
            rate_limiter = ThreadPoolExecutor(max_workers=1)

            # Create a WebSocket connection
            ws = websocket.WebSocketApp(
                'wss://stream.openseabeta.com/socket/websocket?token=28fbebb50f2942b686b48522a76eb9bd',
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                # sslopt={"cert_reqs": ssl.CERT_NONE}
            )

            ws.run_forever()
        except Exception as e:
            logging.error(f'Error in main loop: {e}')
            time.sleep(5)

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

    ticker = time.Ticker(30)
    try:
        for _ in ticker:
            logging.info(f"Sending heartbeat {time.now().strftime('%Y-%m-%d %H:%M:%S')}\n{heartbeat_string}")
            socket.send(heartbeat_string)
    except:
        ticker.close()

if __name__ == '__main__':
    run()