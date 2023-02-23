from selenium import webdriver
import json
from selenium.webdriver.chrome.service import Service


# set the URL to the page you want to scrape
url = "https://core-api.prod.blur.io/v1/collections/boredapeyachtclub/executable-bids?filters=%7B%7D"

# create a new ChromeOptions object
options = webdriver.ChromeOptions()

# set the user agent string to a custom value
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

options.add_argument(r"--user-data-dir=/Users/janusmanlapaz/Library/Application Support/Google/Chrome/")
options.add_argument(r'--profile-directory=Default') 

options.add_argument('--user-agent=' + user_agent)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

service = Service("/opt/homebrew/bin/chromedriver")
# create a new Chrome browser instance with the custom user agent string
driver = webdriver.Chrome(service=service, options=options)

# navigate to the URL
driver.get(url)
# keep the browser open
input("Press enter to quit...")

# # get the page source and convert it to a Python dictionary
# page_source = driver.page_source
# data = json.loads(page_source)

# # save the data to a JSON file
# with open("data.json", "w") as outfile:
#     json.dump(data, outfile)

# # close the browser
# driver.quit()
