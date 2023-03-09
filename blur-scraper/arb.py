from decimal import Decimal
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('./credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'
})

ref = db.reference("records")
records = ref.get()

filtered_records = []

for key in records:
    record = records[key]
    if 'Opensea' in record and 'Blur' in record:
        filtered_records.append(record)

print('potential arbs', len(filtered_records))

potential_arbs = []


for record in filtered_records:
  opensea = record.get('Opensea', {})
  os_top_bid = Decimal(opensea.get('topBid', 0.0))
  
  os_floor = opensea['floorPrice']
  
  if os_floor is None:
    os_floor = 0.0
  
  if isinstance(os_floor, dict):
    os_floor_price = Decimal(os_floor.get('amount', 0.0))
  else:
    os_floor_price = Decimal(os_floor)

  blur = record.get('Blur', {})
  blur_top_bid = Decimal(blur.get('topBid', 0.0))
  blur_floor_price = Decimal(blur.get('floorPrice', 0.0))

  # Check for potential arbitrage opportunities
  if (os_floor_price < blur_top_bid and os_top_bid > blur_floor_price) or (blur_floor_price < os_top_bid and blur_top_bid > os_floor_price):
      potential_arbs.append({
          'contractAddress': record['contractAddress'],
          'Opensea': {
              'topBid': os_top_bid,
              'floorPrice': os_floor_price,
          },
          'Blur': {
              'topBid': blur_top_bid,
              'floorPrice': blur_floor_price,
          }
      })

print('potential arbs', len(potential_arbs))

for arb in potential_arbs:
    print('contract address:', arb['contractAddress'])
    print('Opensea top bid:', arb['Opensea']['topBid'])
    print('Opensea floor price:', arb['Opensea']['floorPrice'])
    print('Blur top bid:', arb['Blur']['topBid'])
    print('Blur floor price:', arb['Blur']['floorPrice'])
    print()
