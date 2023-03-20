from models.Blur import Order, Side, Fee
import json
from eth_account import Account
import hashlib
from web3 import Web3

def main():
    trader = '0xED40E71Ff4AfC90D6a31c25fC162526E1579bA13'
    side = Side.SELL
    matchingPolicy = '0x0000000000daB4A563819e8fd93dbA3b25BC3495'
    collection = '0x062E6604fFA8D4AE459dF58AeC848a2D3171D881'
    tokenId = 1999
    amount = 1
    paymentToken = '0x0000000000000000000000000000000000000000'
    price = 43000000000000000 # 0.043 ETH
    listingTime = 1678889509
    expirationTime = 1679494309
    fees = [
        Fee( rate=666, recipient='0xEE5B587D7Eb281A45aeF13e7bC5E6A36178b3139')
    ]
    salt = 134937004207775963615068463729806133349

    extraParams = '0x01'
    nonce = 0

    order = Order(
        trader=trader,
        side=side,
        matchingPolicy=matchingPolicy,
        collection=collection,
        tokenId=tokenId,
        amount=amount,
        paymentToken=paymentToken,
        price=price,
        listingTime=listingTime,
        expirationTime=expirationTime,
        fees=fees,
        salt=salt,
        extraParams=extraParams,
        nonce=nonce
    )

    private_key = 'Private key here'
    
    message_str = json.dumps(order.dict(), separators=(',', ':'))
    wallet = Account.from_key(private_key)
    message_hash = hashlib.sha3_256(message_str.encode('utf-8')).digest()
    eth_message = f"\x19Ethereum Signed Message:\n{len(message_hash)}{message_hash.hex()}"
    eth_message_hash = hashlib.sha3_256(eth_message.encode('utf-8')).digest()
    signed_message = wallet.signHash(Web3.toBytes(hexstr=eth_message_hash.hex()))

    signature = f"{signed_message['r'].hex()}{signed_message['s'].hex()}{signed_message['v'].to_bytes(1, 'big').hex()}"

if __name__ == '__main__':
    main()