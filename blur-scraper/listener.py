import websocket
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime, timedelta
import logging
import time



EXPIRATION_TIME = (datetime.now() + timedelta(days=1)).isoformat()

def on_message(ws, message):
    try:
        # Check for keep alive message, if received send back "3"
        if message == "2":
            ws.send("3")
        else:
            data = json.loads(message[2:]) # remove prefix "42" and parse JSON
            if isinstance(data, dict) and "sid" in data:
                # ignore messages with a "sid" key
                return
            elif data[0].endswith(".collectionBidStats"):
                on_collection_bid(data)
            elif data[0].endswith("stats.floorUpdate"):
                on_floor_update(data)
    except json.JSONDecodeError:
        pass
    except Exception as e:
        print("Error in on_message:", e)


def on_collection_bid(data):
  contract_address = data[1]["contractAddress"]
  bid_data = data[1]
  best_price = float(bid_data["bestPrice"])

  ref = db.reference(f"records/{contract_address}")

  record_data = ref.get()

  if record_data is not None:
      current_best_price = float(record_data.get("Blur", {}).get("topBid", 0))
      if best_price != current_best_price:
          # Update the "bids" property in the "Blur" object
          record_data.update({"Blur": {"bidPayload": bid_data, "topBid": best_price}}, expires=json.loads(json.dumps(EXPIRATION_TIME)))
          ref.update(record_data)
          print(f"Updated Blur top bid for contract address {contract_address}")

def on_floor_update(data):
  try:
    contract_address = data[1]["contractAddress"]
    floor_update_data = data[1]
    
    if isinstance(floor_update_data, str) or floor_update_data is None:
       print("floor_update_data is a string or None", floor_update_data)
       return
    
    floor0 = floor_update_data.get("floor0")

    if floor0 is None:
        print("floor0 is None")
        return
    
    marketplace = floor0["marketplace"]

    ref = db.reference(f"records/{contract_address}")
    record_data = ref.get()

    if marketplace == "OPENSEA":
        current_floor_price = float(record_data.get("Opensea", {}).get("floorPrice", {}).get("amount", "0"))
        if current_floor_price != float(floor0["amount"]):
          print("Updating Opensea floor price for contract address ", contract_address)
          record_data.update({"Opensea": {"askPayload": floor_update_data, "floorPrice": floor0['amount']}}, expires=json.loads(json.dumps(EXPIRATION_TIME)))
          ref.update(record_data)

    elif marketplace == "BLUR":
        current_floor_price = float(record_data.get("Blur", {}).get("floorPrice", {}).get("amount", "0"))
        if current_floor_price != float(floor0["amount"]):
          print("Updating Blur floor price for contract address ", contract_address)
          record_data.update({"Blur": {"askPayload": floor_update_data, "floorPrice": floor0['amount']}}, expires=json.loads(json.dumps(EXPIRATION_TIME)))
          ref.update(record_data)
  except Exception as e:
    print("Error in on_floor_update:", e)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, code, reason):
    logging.info('Disconnected from server')
    logging.error(f'Code: {code}, Reason: {reason}')
    # Attempt to reconnect
    while True:
        try:
            logging.info('Attempting to reconnect...')
            ws.run_forever()
        except Exception as e:
            logging.error(f'Error while reconnecting: {e}')
            time.sleep(5)

def on_open(ws):
    # send message "40" when the connection is established
    ws.send("40")
    cred = credentials.Certificate('./credentials.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'
    })
    ws.send('4216["subscribe",["stats.floorUpdate", "denormalizer.collectionBidStats"]]')

if __name__ == "__main__":
    websocket.enableTrace(False)
    ws_url = "wss://feeds.prod.blur.io/socket.io/?tabId=jvP08hWrhRHy&storageId=Lvlg49tHpB7j&EIO=4&transport=websocket"
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    ws.run_forever()
