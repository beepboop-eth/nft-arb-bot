import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import glob

# Load the Firebase credentials file
cred = credentials.Certificate('./credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'
})

# Get a reference to the Realtime Database
ref = db.reference('records')

# Iterate through all JSON files in the collections folder
for filename in glob.glob('collections/*.json'):
    with open(filename, 'r') as f:
        data = json.load(f)
        # Loop through the collections array and upsert each contract address
        for collection in data['collections']:
            ref.child(collection['contractAddress']).update({'BlurCollectionSlug': collection['collectionSlug']})
            print('Upserted successfully', collection['contractAddress'])