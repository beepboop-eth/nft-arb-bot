import argparse
import json
import pyperclip

# Set up command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("index", type=int, help="index of the JSON file to read")
args = parser.parse_args()

# Construct the filename for the JSON file to read
filename = f"collections/{args.index}.json"

# Load the data from the JSON file
with open(filename, "r") as f:
    data = json.load(f)

# Extract the contract address and volume one day amount from the last collection
last_collection = data["collections"][-1]
contract_address = last_collection["contractAddress"]
volume_one_day_amount = last_collection["volumeOneDay"]["amount"]
print("contract address:", contract_address)
print("volume one day amount:", volume_one_day_amount)
# Construct the URL for the next 100 collections API call
next_url = f'https://core-api.prod.blur.io/v1/collections/?filters={{"cursor":{{"contractAddress":"{contract_address}","volumeOneDay":"{volume_one_day_amount}"}},"sort":"VOLUME_ONE_DAY","order":"DESC"}}'

# Copy the URL to the clipboard
pyperclip.copy(next_url)
