from decimal import Decimal
from db import initialize_database
from firebase_admin import db

OPENSEA_FEE = Decimal('0.005')

def calculate_collection_royalties(marketplace_fees, marketplacePath, collection_fee_basis_points):
    collection_royalties = collection_fee_basis_points / Decimal('10000')
    for entry in marketplacePath:
        marketplace_fees += Decimal(str(entry.get("price", Decimal('0')))) * collection_royalties
    return marketplace_fees

def get_marketplace_fees(contract_address, marketplacePath): 
    initialize_database()
    
    ref = db.reference(f"fees/{contract_address}")
    record = ref.get()

    if record is None:
        print('No fee record found for contract address: ', contract_address)
        return Decimal('0')
    
    marketplace_fees = Decimal('0')

    contains_opensea = lambda arr: any(entry["marketplace"] == "OPENSEA" for entry in arr)
    if contains_opensea(marketplacePath):
        get_opensea = lambda arr: next((entry for entry in arr if entry["marketplace"] == "OPENSEA"), None)
        price = Decimal(str(get_opensea(marketplacePath).get("price", 0)))
        marketplace_fees += price * OPENSEA_FEE     


    return calculate_collection_royalties(marketplace_fees, marketplacePath, Decimal(record.get('fee', Decimal('0'))))
