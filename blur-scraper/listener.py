import websocket
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

def on_message(ws, message):
    # print(f"Received message: {message}")
    try:
        data = json.loads(message[2:]) # remove prefix "42" and parse JSON
        if data[0].endswith(".collectionBidStats"):
          on_collection_bid(data)
        elif data[0].endswith(".stats.floorUpdate"):
          on_floor_update(data)
    except json.JSONDecodeError:
        pass

def on_collection_bid(data):
  contract_address = data[0].split(".")[0]
  bid_data = data[1]
  best_price = float(bid_data["bestPrice"])

  ref = db.reference(f"records/{contract_address}")

  record_data = ref.get()

  if record_data is not None:
      # If the record exists, update the "bestPrice" and "Blur" properties
      current_best_price = float(record_data.get("Blur", {}).get("bestPrice", 0))
      if best_price != current_best_price:
          # Update the "bids" property in the "Blur" object
          record_data.update({"topBid": best_price, "Blur": {"bids": [bid_data]}})
          ref.update(record_data)
          print(f"Updated record for contract address {contract_address}")
      # else:
      #     # Overwrite the existing "bids" property in the "Blur" object
      #     record_data.get("Blur", {})["bids"] = [bid_data]
      #     ref.update(record_data)
      #     print(f"Overwrote bids data for contract address {contract_address}")
  else:
      # If the record doesn't exist yet, create it with the "bestPrice" and "Blur" properties
      ref.set({"bestPrice": best_price, "Blur": {"bids": [bid_data]}})
      print(f"Created record for contract address {contract_address}")

def on_floor_update(data):
  contract_address = data[0].split(".")[0]
  floor_update_data = data[1]
  floor0 = floor_update_data.get("floor0")
  floor1 = floor_update_data.get("floor1")

  ref = db.reference(f"records/{contract_address}")
  record_data = ref.get()

  if record_data is not None:
      # If the record exists, update the "Blur" property with the new "asks" data if it has changed
      blur_data = record_data.get("Blur", {})
      asks = blur_data.get("asks", {})
      if floor0 and floor0["amount"] != asks.get("openseaPrice"):
          blur_data["openseaAsks"] = {"price": floor0["amount"], "marketplace": floor0["marketplace"]}
          record_data["Blur"] = blur_data
          ref.update(record_data)
          print(f"Updated asks data for contract address {contract_address}")
      elif floor1 and (not asks or floor1["amount"] != asks.get("blurPrice")):
          blur_data["blurAsks"] = {"price": floor1["amount"], "marketplace": floor1["marketplace"]}
          record_data["Blur"] = blur_data
          ref.update(record_data)
          print(f"Updated asks data for contract address {contract_address}")
      else:
          print(f"No floor price change for contract address {contract_address}")
  else:
      # If the record doesn't exist yet, create it with the "Blur" property and the new "asks" data
      blur_data = {"asks": {}}
      if floor0:
          blur_data["openseaAsks"]["price"] = floor0["amount"]
          blur_data["openseaAsks"]["marketplace"] = floor0["marketplace"]
      elif floor1:
          blur_data["blurAsks"]["price"] = floor1["amount"]
          blur_data["blurAsks"]["marketplace"] = floor1["marketplace"]
      ref.set({"Blur": blur_data})
      print(f"Created record for contract address {contract_address}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    # send message "40" when the connection is established
    ws.send("40")
    cred = credentials.Certificate('./credentials.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'
    })

    # # Get a reference to the Realtime Database
    # ref = db.reference('records')
    
    # # Retrieve all records in the "records" node
    # all_records = ref.get()
    # # Filter records that have the "BlurCollectionSlug" property
    # records_with_slug = {k: v for k, v in all_records.items() if 'BlurCollectionSlug' in v}
    # print('# of Blur collections', len(records_with_slug.items()))

    # # Get a reference to the Realtime Database
    # ref = db.reference('records')
    ws.send('4216["subscribe",["0xe2e27b49e405f6c25796167b2500c195f972ebac.stats.floorUpdate", "0xe2e27b49e405f6c25796167b2500c195f972ebac.denormalizer.collectionBidStats"]]')

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws_url = "wss://feeds.prod.blur.io/socket.io/?tabId=jvP08hWrhRHy&storageId=Lvlg49tHpB7j&EIO=4&transport=websocket"
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    ws.run_forever()
