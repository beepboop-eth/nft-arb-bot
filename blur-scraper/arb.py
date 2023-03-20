from decimal import Decimal
from fees import get_marketplace_fees
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from gas import get_gas_fee, BLUR, OPENSEA
from db import initialize_database
from decimal import Decimal

BLACKLIST_CONTRACTS = ['0x2b0bfa93beb22f44e7c1be88efd80396f8d9f1d4', '0x672664ccad533401066ebb70361c93c4ca567de0', '0x672664ccad533401066ebb70361c93c4ca567de0']

def get_potential_arbs():
  ref = db.reference("records")
  records = ref.get()

  filtered_records = []

  for key in records:
      record = records[key]
      if 'Opensea' in record and 'Blur' in record:
          record['contractAddress'] = key
          filtered_records.append(record)

  return filtered_records


def get_spread_after_fees(contract_address, top_bid, floor_price, marketplace_path):
    gas_fee = get_gas_fee(marketplace_path)['average']
    marketplace_fees = get_marketplace_fees(contract_address, marketplace_path)
    gas_settings = {
        "maxPriorityFeePerGas": gas_fee['maxPriorityFeePerGas'],
        "maxFeePerGas": gas_fee['maxFeePerGas']
    }

    return top_bid - floor_price - gas_fee['value'] - marketplace_fees, gas_fee['value'], gas_settings, marketplace_fees

def does_arb_exist(filtered_records):
    buy_on_blur_arbs = []
    buy_on_os_arbs = []

    for record in filtered_records:
        opensea = record.get('Opensea', {})
        os_top_bid = Decimal(opensea.get('topBid', 0.0))
        os_timestamp = opensea.get('timestamp', '')

        os_floor = opensea.get('floorPrice')

        if os_floor is None:
            os_floor = 0.0

        if isinstance(os_floor, dict):
            os_floor_price = Decimal(os_floor.get('amount', 0.0))
        else:
            os_floor_price = Decimal(os_floor)

        blur = record.get('Blur', {})
        blur_top_bid = Decimal(blur.get('topBid', 0.0))
        blur_floor_price = Decimal(blur.get('floorPrice', 0.0))
        blur_timestamp = blur.get('timestamp', '')

        # Check for potential arbitrage opportunities
        contract_address = record.get('ContractAddress', record.get('contractAddress', ''))

        if (os_top_bid > blur_floor_price and os_top_bid > 0 and blur_floor_price > 0):
            marketplace_path = [
                { "marketplace": "OPENSEA", "price": os_top_bid },
                { "marketplace": "BLUR", "price": blur_floor_price }
            ]
            spread, gas_fee, gas_settings, marketplace_fees = get_spread_after_fees(contract_address, os_top_bid, blur_floor_price, marketplace_path)
            buy_on_blur_arbs.append({
                'contractAddress': contract_address,
                'topBid': os_top_bid,
                'floorPrice': blur_floor_price,
                'spreadRaw': os_top_bid - blur_floor_price,
                'spreadPercentageRaw': (os_top_bid - blur_floor_price) / blur_floor_price * 100,
                'spreadAfterFees': spread,
                'spreadPercentageAfterFees': spread / blur_floor_price * 100,
                'gasFee': gas_fee,
                'marketplaceFees': marketplace_fees,
                'gasSettings': gas_settings,
                'timestamptopBid': os_timestamp,
                'timestampfloorPrice': blur_timestamp,
            })
        elif (blur_top_bid > os_floor_price and blur_top_bid > 0 and os_floor_price > 0):
            marketplace_path = [
                { "marketplace": "BLUR", "price": blur_top_bid },
                { "marketplace": "OPENSEA", "price": os_floor_price }
            ]
            spread, gas_fee, gas_settings, marketplace_fees = get_spread_after_fees(contract_address, blur_top_bid, os_floor_price, marketplace_path)
            buy_on_os_arbs.append({
                'contractAddress': contract_address,
                'topBid': blur_top_bid,
                'floorPrice': os_floor_price,
                'spreadRaw': blur_top_bid - os_floor_price,
                'spreadPercentageRaw': (blur_top_bid - os_floor_price) / os_floor_price * 100,
                'spreadAfterFees': spread,
                'spreadPercentageAfterFees': spread / os_floor_price * 100,
                'gasFee': gas_fee,
                'marketplaceFees': marketplace_fees,
                'gasSettings': gas_settings,
                'timestamptopBid': blur_timestamp,
                'timestampfloorPrice': os_timestamp,
            })

    return buy_on_blur_arbs, buy_on_os_arbs

def calculate_arb_spread(potential_arbs):
  print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

  filtered_potential_arbs = filter(lambda x: x['contractAddress'] not in BLACKLIST_CONTRACTS, potential_arbs)
  for arb in filtered_potential_arbs:
      if arb['spreadAfterFees'] > 0:
        contract_address = arb['contractAddress']
        print('contract address:', contract_address)
        print('Top bid:', arb['topBid'])
        print('Timestamp top bid:', arb['timestamptopBid'])
        print('Floor price:', arb['floorPrice'])
        print('Timestamp floor price:', arb['timestampfloorPrice'])
        print('Raw price difference:', arb['spreadRaw'])
        print('Raw percentage price difference: ' + str(arb['spreadPercentageRaw']) + '%')
        print('Price difference after fees:', arb['spreadAfterFees'])
        print('Percentage price difference after fees: ' + str(arb['spreadPercentageAfterFees']) + '%')
        print('Gas fee:', arb['gasFee'])
        print('Marketplace fees:', arb['marketplaceFees'])
        print('Gas settings:', arb['gasSettings'])
        print('------------------------------------')
      # for arb in potential_arbs:
      #   contract_address = arb['contractAddress']
      #   print('contract address:', contract_address)
      #   print('Top bid:', arb['topBid'])
      #   print('Floor price:', arb['floorPrice'])
      #   print('Raw price difference:', arb['spreadRaw'])
      #   print('Raw percentage price difference: ' + str(arb['spreadPercentageRaw']) + '%')
      #   print('Price difference after fees:', arb['spreadAfterFees'])
      #   print('Percentage price difference after fees: ' + str(arb['spreadPercentageAfterFees']) + '%')
      #   print('Gas fee:', arb['gasFee'])
      #   print('Marketplace fees:', arb['marketplaceFees'])
      #   print('Gas settings:', arb['gasSettings'])
      #   print('------------------------------------')
  print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
def main():
  print('Calculating arb...')
  initialize_database()
  # print(get_marketplace_fees([{ "marketplace": BLUR, "price": 1.0}, { "marketplace": OPENSEA, "price": 1.5}], '0x00000000001ba87a34f0d3224286643b36646d81'))
  print('Initialized database, finding potential arbs...')
  filtered_records = get_potential_arbs()
  print('Potential arbs', len(filtered_records))

  buy_on_blur_arbs, buy_on_os_arbs = does_arb_exist(filtered_records)

  print('Buy on blur, sell on Opensea', len(buy_on_blur_arbs))
  calculate_arb_spread(buy_on_blur_arbs)

  print('Buy on Opensea, sell on blur', len(buy_on_os_arbs))
  calculate_arb_spread(buy_on_os_arbs)

  print('Total arbs found:', len(buy_on_blur_arbs) + len(buy_on_os_arbs))
  print('Total profitable arbs found after fees: ', len(list(filter(lambda x: x['spreadAfterFees'] > 0, buy_on_blur_arbs))) + len(list(filter(lambda x: x['spreadAfterFees'] > 0, buy_on_os_arbs))))

if __name__ == '__main__':
    main()