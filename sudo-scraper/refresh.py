import logging
from db.client import initialize_database
from firebase_admin import db as firebaseDb

def main():
    firebaseDatabase = initialize_database()
    print("Retrieving records...")
    refresh_opensea_offers(firebaseDatabase)

def refresh_opensea_offers(db_client: firebaseDb._Client):
    # Reference to the root of the database
    root_ref = db_client.reference("/")
    
    # Get a reference to the node containing the records
    records_ref = root_ref.child("records")
    
    # Get all records from the database
    records = records_ref.get()
    print("Retrieved records: ", len(records))
    
    # Iterate through all records and delete the Opensea property from each one
    for key in records:
        record_ref = records_ref.child(key)
        opensea_ref = record_ref.child("Opensea")
        if opensea_ref.get() is not None:
            print("Deleting Opensea property from record: ", key)
            opensea_ref.delete()
    
    logging.info("Successfully refreshed Opensea offers")

if __name__ == "__main__":
    main()