import math
import random
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from ratelimit import limits, sleep_and_retry
import os
import json
import logging
import requests
from dotenv import load_dotenv, dotenv_values

def main():
  cred = credentials.Certificate('./credentials.json')
  firebase_admin.initialize_app(cred, {
      'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'
  })
  load_dotenv()
  ref = db.reference("records")
  records = ref.get()

  filtered_records = []

  for key in records:
      record = records[key]
      if 'OpenseaCollectionSlug' not in record or record['OpenseaCollectionSlug'] == '':
          record['contractAddress'] = key
          filtered_records.append(record)
  print('found ', len(filtered_records), ' records to update')

  for filtered_record in filtered_records:
    contract_address = filtered_record['contractAddress']


    retries = 5
    for i in range(retries):
        try:
            if i > 0:
              print('retrying for ', contract_address, ' attempt ', i)
            collection_slug = get_collection_slug(contract_address)
            break
        except:
            backoff = math.pow(2, i) + (random.randint(0, 1000) / 1000)
            time.sleep(backoff)

    record_ref = db.reference(f"records/{contract_address}")
    record_data = record_ref.get()
    record_data.update({'OpenseaCollectionSlug': collection_slug})
    record_ref.update(record_data)
    print('Updated record successfully ', contract_address)

@sleep_and_retry
@limits(calls=3, period=1)
def get_collection_slug(contract_address):
    # Construct the URL for the request to the OpenSea API
  url = f"https://api.opensea.io/api/v1/asset_contract/{contract_address}"

  # Set up the HTTP headers
  headers = {
      "Content-Type": "application/json",
      "X-API-KEY": dotenv_values(".env")["OPENSEA_API_KEY"],
  }

  # Make the request
  try:
      response = requests.get(url, headers=headers)
      response.raise_for_status()
  except requests.exceptions.RequestException as e:
      logging.error(f"Unable to make request to Opensea API: {e}")
      return f"Unable to make request to Opensea API: {e}"

  # Parse the response to retrieve the collection slug
  result = json.loads(response.text)

  # Get the collection object from the response
  collection = result.get("collection")
  if not isinstance(collection, dict):
      return "Unable to get collection object"

  # Get the collection slug from the collection object
  collection_slug = collection.get("slug")
  if not isinstance(collection_slug, str):
      return "Unable to get collection slug"

  return collection_slug

if __name__ == '__main__':
  main()