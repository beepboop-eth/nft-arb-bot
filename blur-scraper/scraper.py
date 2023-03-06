from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Set up Firefox profile
profile = webdriver.FirefoxProfile("/Users/janusmanlapaz/Library/Application Support/Firefox/Profiles/25q66lbr.default-release-1")

# Launch Firefox and go to the URL
driver = webdriver.Firefox(firefox_profile=profile)
base_url = 'view-source:https://core-api.prod.blur.io/v1/collections/?filters={%22sort%22:%20%22VOLUME_ONE_DAY%22,%22order%22:%20%22DESC%22}'
driver.get(base_url)

# # Extract the contract address and volume one day amount from the last collection
# last_collection = data["collections"][-1]
# contract_address = last_collection["contractAddress"]
# volume_one_day_amount = last_collection["volumeOneDay"]["amount"]

# print("contract address:", contract_address)
# print("volume one day amount:", volume_one_day_amount)

# next_url = f'view-source:https://core-api.prod.blur.io/v1/collections/?filters={{"cursor":{{"contractAddress":"{contract_address}","volumeOneDay":"{volume_one_day_amount}"}},"sort":"VOLUME_ONE_DAY","order":"DESC"}}'

# Get the JSON data from the page content
pre = driver.find_element(By.TAG_NAME, 'pre')
data = json.loads(pre.text)

# Save the data to a file
with open('collections/0.json', 'w') as f:
    json.dump(data, f, indent=2)
# driver.close
# Extract the contract address and volume one day amount from the last collection
last_collection = data["collections"][-1]
contract_address = last_collection["contractAddress"]
volume_one_day_amount = last_collection["volumeOneDay"]["amount"]

print("contract address:", contract_address)
print("volume one day amount:", volume_one_day_amount)

next_url = f'view-source:https://core-api.prod.blur.io/v1/collections/?filters={{"cursor":{{"contractAddress":"{contract_address}","volumeOneDay":"{volume_one_day_amount}"}},"sort":"VOLUME_ONE_DAY","order":"DESC"}}'

i = 1

while len(data["collections"]) > 0: 
  driver.get(next_url)
  pre = driver.find_element(By.TAG_NAME, 'pre')
  data = json.loads(pre.text)
  with open(f'collections/{i}.json', 'w') as f:
    json.dump(data, f, indent=2)
    print(f'Data saved to {i}.json')
  last_collection = data["collections"][-1]
  contract_address = last_collection["contractAddress"]
  volume_one_day_amount = last_collection["volumeOneDay"]["amount"]
  print("contract address:", contract_address)
  print("volume one day amount:", volume_one_day_amount)  
  next_url = f'view-source:https://core-api.prod.blur.io/v1/collections/?filters={{"cursor":{{"contractAddress":"{contract_address}","volumeOneDay":"{volume_one_day_amount}"}},"sort":"VOLUME_ONE_DAY","order":"DESC"}}'
  i += 1
