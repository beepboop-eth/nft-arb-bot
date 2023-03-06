from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Set up Firefox profile
profile = webdriver.FirefoxProfile("/Users/janusmanlapaz/Library/Application Support/Firefox/Profiles/25q66lbr.default-release-1")

# Launch Firefox and go to the URL
driver = webdriver.Firefox(firefox_profile=profile)
driver.get('view-source:https://core-api.prod.blur.io/v1/collections')

# Get the JSON data from the page content
pre = driver.find_element(By.TAG_NAME, 'pre')
json_data = json.loads(pre.text)

# Save the data to a file
with open('data.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print('Data saved to data.json')
