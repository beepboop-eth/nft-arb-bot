import http
import json
import logging
import time
from db.client import initialize_database
from models.Sudo import CollectionItem, CollectionsData, CollectionsResponse, pydantic_encoder
from firebase_admin import db as firebaseDb
from ratelimit import limits, sleep_and_retry
from dotenv import load_dotenv, dotenv_values
import requests
from typing import List
from requests.exceptions import HTTPError


def main():
  print("Scraping Sudo...")
  load_dotenv()
  scrape_sudo()

def scrape_sudo():
  visited = set()
  firebaseDatabase = initialize_database()
  downloadCollections(visited, firebaseDatabase, "b7b0423cdec1ed60fc29270c951be64dEfblA+A95zk6anwkAEPi9w==")

def downloadCollections(visited, firebaseDatabase, cursor=None):
  while True:
    if cursor in visited:
      print(f"Cursor {cursor} already visited, breaking out of loop")
      break
    
    visited.add(cursor)
    print("Downloading from cursor", cursor)
    # Set up the GraphQL query
    query = '''query ($cursor: String) {
      getNftPoolCollectionsByExchange(
        exchangeAddress: "0xb16c1342E617A5B6E4b631EB114483FDB289c0A4",
        networkId: 1,
        cursor: $cursor
      ) {
        items {
          balanceNBT
          collectionAddress
          collectionId
          exchangeAddress
          exchangeId
          floorNBT
          media {
            image
            thumbLg
            thumbSm
          }
          name
          networkId
          nftBalance
          nftVolumeAllTime
          offerNBT
          volumeAllTimeNBT
        }
        cursor
      }
    }'''

    # Set up the variables for the GraphQL query
    variables = {
      "cursor": cursor
    }

    collections_response = None

    resp = make_request(query, variables)
    if resp.status_code != 200:
        print("Error making request: ", resp.reason)
        return

    body = resp.content

    raw_response = json.loads(body.decode("utf-8"))["data"]["getNftPoolCollectionsByExchange"]
    collections_response = CollectionsData.parse_obj(raw_response)
    items = collections_response.items
    cursor = collections_response.cursor
        # Check if items and cursor are not None
    if items is not None and cursor is not None:
      print("Writing items to database...")
      print("First item: ", items[0].collectionAddress)
      writeItemsToDatabase(items, firebaseDatabase)
    else:
      print("No more data to download")
      break

def writeItemsToDatabase(items, firebaseDatabase):
    # Reference to the root of the database
    root_ref = firebaseDatabase.reference("/")

    # Get a reference to the node containing the records
    records_ref = root_ref.child("records")

    # Batch reads and writes
    updates = {}
    for item in items:
        collection_address = item.collectionAddress

        # Merge Sudoswap data with existing data
        existing_data = records_ref.child(collection_address).get()
        if existing_data is None:
            existing_data = {}
        existing_data["Sudoswap"] = json.loads(json.dumps(item.dict(), default=pydantic_encoder))
        updates[collection_address] = existing_data

    # Write updates to the database
    records_ref.update(updates)

@sleep_and_retry
@limits(calls=500, period=1)
def make_request(query, variables):
    url = "https://api.defined.fi"
    
    # Create the request payload
    payload = {
        "query": query,
        "variables": variables
    }

    # Create the HTTP request headers
    headers = {
        "Content-Type": "application/json",
        "x-api-key": dotenv_values(".env")["DEFINED_API_KEY"]
    }

    # Make the request
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

if __name__ == "__main__":
    main()