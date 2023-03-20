from db import initialize_database
from firebase_admin import db


def main():
  initialize_database()
  ref = db.reference("records")
  records = ref.get()

  updates = {}
  for record_key in records:
    record = records[record_key]

    if "Blur" in record:
      del record["Blur"]
    if "Opensea" in record:
      del record["Opensea"]

    updates[record_key] = record
    print('Record updated', record_key)

  ref.update(updates)
  print("Blur and Opensea properties deleted for all records")

if __name__ == '__main__':
    main()
