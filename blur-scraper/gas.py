from decimal import Decimal
import requests
from cachetools import cached, TTLCache
from dotenv import load_dotenv, dotenv_values

FULFILL_ORDER_BLUR_GAS = Decimal('284418.5')

# BASIC for ETH Trades, ADVANCED For WETH Trades
FULFILL_ORDER_OPENSEA_GAS_BASIC = Decimal('142623.50')
FULFILL_ORDER_OPENSEA_GAS_ADVANCED = Decimal('274129.78')
SET_APPROVAL_GAS = Decimal('46521.89')
BLUR = 'BLUR'
OPENSEA = 'OPENSEA'

# set up a cache with a TTL of 5 seconds
cache = TTLCache(maxsize=1, ttl=5)

@cached(cache)
def get_gas_price():
    headers = {
        "Authorization": dotenv_values(".env")["BLOCKNATIVE_API_KEY"]
    }

    url = "https://api.blocknative.com/gasprices/blockprices"

    response = requests.get(url, headers=headers)


    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        max_price = data["maxPrice"] + 1

        fast_price = None
        average_price = None

        for estimated_price in data["blockPrices"][0]["estimatedPrices"]:
            if fast_price is None and estimated_price["confidence"] == 99:
                fast_price = estimated_price
            elif average_price is None and estimated_price["confidence"] == 90:
                average_price = estimated_price
            elif fast_price is not None and average_price is not None:
                break
        
        return {
            "fastest": max_price,
            "fast": fast_price,
            "average": average_price
        }
    else: 
        print('Failed to retrieve gas prices:', response.status_code)
        raise

# Gas Fee = SetApprovalForAll_Gas * Gas Price + FulfillOrder_Gas_Buy_Marketplace * Gas Price + FulfillOrder_Gas_Sell_Marketplace * Gas Price
def get_gas_fee(marketplace_path):
    gas_price = get_gas_price()
    fastest_price = gas_price["fastest"]
    fast_price = gas_price["fast"]["price"]
    average_price = gas_price["average"]["price"]
    
    market_fees = {
        BLUR: {
            "fulfill_order_gas": FULFILL_ORDER_BLUR_GAS,
            "fulfill_order_price": {
                "fastest": fastest_price,
                "fast": fast_price,
                "average": average_price
            }
        },
        OPENSEA: {
            "fulfill_order_gas": FULFILL_ORDER_OPENSEA_GAS_ADVANCED,
            "fulfill_order_price": {
                "fastest": fastest_price,
                "fast": fast_price,
                "average": average_price
            }
        }
    }
    
    fees = {
        "fastest": {
            "value": Decimal('0'),
            "maxPriorityFeePerGas": gas_price["fast"]["maxPriorityFeePerGas"],
            "maxFeePerGas": gas_price["fast"]["maxFeePerGas"]
        },
        "fast": {
            "value": Decimal('0'),
            "maxPriorityFeePerGas": gas_price["fast"]["maxPriorityFeePerGas"],
            "maxFeePerGas": gas_price["fast"]["maxFeePerGas"]
        },
        "average": {
            "value": Decimal('0'),
            "maxPriorityFeePerGas": gas_price["average"]["maxPriorityFeePerGas"],
            "maxFeePerGas": gas_price["average"]["maxFeePerGas"]
        }
    }

    for i, entry in enumerate(marketplace_path):
        marketplace = entry["marketplace"]
        # if i is even, then we are buying on that marketplace, else selling
        if i % 2 == 0:
            fulfill_order_gas = market_fees[marketplace]["fulfill_order_gas"]
            fulfill_order_price = market_fees[marketplace]["fulfill_order_price"]
            
            fees["fastest"]["value"] += fulfill_order_gas * fulfill_order_price["fastest"]
            fees["fast"]["value"] += fulfill_order_gas * fulfill_order_price["fast"]
            fees["average"]["value"] += fulfill_order_gas * fulfill_order_price["average"]
        else:
            fees["fastest"]["value"] += SET_APPROVAL_GAS * fastest_price
            fees["fast"]["value"] += SET_APPROVAL_GAS * fast_price
            fees["average"]["value"] += SET_APPROVAL_GAS * average_price
            
            fulfill_order_gas = market_fees[marketplace]["fulfill_order_gas"]
            fulfill_order_price = market_fees[marketplace]["fulfill_order_price"]
            
            fees["fastest"]["value"] += fulfill_order_gas * fulfill_order_price["fastest"]
            fees["fast"]["value"] += fulfill_order_gas * fulfill_order_price["fast"]
            fees["average"]["value"] += fulfill_order_gas * fulfill_order_price["average"]
    
    fees["fastest"]["value"] /= Decimal('10') ** 9
    fees["fast"]["value"] /= Decimal('10') ** 9
    fees["average"]["value"] /= Decimal('10') ** 9
    
    return fees

