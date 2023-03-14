import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

isInitialized = False
def initialize_database():
  global isInitialized
  if not isInitialized:
    cred = credentials.Certificate('./credentials.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://nft-arb-bot-default-rtdb.firebaseio.com/'
    })
    isInitialized = True
