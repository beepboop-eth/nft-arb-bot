# nft-arb-bot
## Refresh Script

This Python script refreshes the Opensea offers in a Firebase Realtime Database. It uses the Firebase Admin SDK for Python and the `firebase-admin` package to authenticate with Firebase and access the database. 

### Prerequisites

To use this script, you will need to have the following:

- Python 3.x installed on your system
- A Firebase project with a Realtime Database
- A `credentials.json` file for your Firebase project in the same directory as the `refresh.py` script
- The `firebase-admin` package installed (you can install it via pip)

### Usage

To use this script, follow these steps:

1. Open the `refresh.py` script in a text editor or IDE.
2. Modify the `credentials.json` file path in the `initialize_database()` function to point to the location of your own credentials file.
3. Run the script by typing `python refresh.py` in the command line.
4. The script will retrieve all records from the `records` node in the database and delete the `Opensea` property from each record.
5. The script will log a message to the console when it is finished.

### License

This code is released under the MIT License. See LICENSE for more information.
