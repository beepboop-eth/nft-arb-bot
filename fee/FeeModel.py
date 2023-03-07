import firebase_admin
from firebase_admin import credentials, db

class OpenSea:
    platform_fee = 250

class Blur:
    platform_fee = 0

class CollectionFee:
    def get_collection_fee(contract):
        contract = contract.lower()
        cred = credentials.Certificate("credentials.json")
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'})
        return db.reference(f"fees/{contract}").get()["fee"]

class Utils:
    def to_decimal(bps):
        return bps/1e4
    
if __name__ == "__main__":
    bayc_fee = CollectionFee.get_collection_fee("0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D")
    os_fee = OpenSea.platform_fee
    total_fee = Utils.to_decimal(bayc_fee + os_fee)
    print(total_fee)
    
    





