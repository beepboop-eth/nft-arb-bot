import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

def initialize_database():
    cred = credentials.Certificate('credentials.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'
    })
    return db
