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
        record['contractAddress'] = key
        filtered_records.append(record)

print('potential arbs', len(filtered_records))

potential_arbs = []

for record in filtered_records:
    opensea = record.get('Opensea', {})
    os_top_bid = Decimal(opensea.get('topBid', 0.0))

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

    # Check for potential arbitrage opportunities
    contract_address = record.get('ContractAddress', record.get('contractAddress', ''))

    if ((os_top_bid > blur_floor_price and os_top_bid > 0 and blur_floor_price > 0)  or (blur_top_bid > os_floor_price and blur_top_bid > 0 and os_floor_price > 0)) :
        potential_arbs.append({
            'contractAddress': contract_address,
            'Opensea': {
                'topBid': os_top_bid,
                'floorPrice': os_floor_price,
            },
            'Blur': {
                'topBid': blur_top_bid,
                'floorPrice': blur_floor_price,
            }
        })

for arb in potential_arbs:
    contract_address = arb['contractAddress']
    os_spread = arb['Opensea']['topBid'] -  arb['Blur']['floorPrice']
    blur_spread = arb['Blur']['topBid'] - arb['Opensea']['floorPrice']

    isBuyOs = os_spread > 0
    isBuyBlur = blur_spread > 0

    print('contract address:', contract_address)

    if isBuyOs:
        print('Buy on Opensea, sell on blur')
        print('Raw price difference:', os_spread)
        print('Opensea top bid:', arb['Opensea']['topBid'])
        print('Blur floor price:', arb['Blur']['floorPrice'])
        print('Percentage price difference: ' + str(os_spread / arb['Blur']['floorPrice'] * 100) + '%')
    elif isBuyBlur:
        print('Buy on blur, sell on Opensea')
        print('Blur top bid:', arb['Blur']['topBid'])
        print('Opensea floor price:', arb['Opensea']['floorPrice'])
        print('Raw price difference:', blur_spread)
        print('Percentage price difference: ' + str(blur_spread / arb['Opensea']['floorPrice'] * 100) + '%')
    print('------------------------------------')
print('potential arbs', len(potential_arbs))
