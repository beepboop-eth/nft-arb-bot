from pydantic import BaseModel
from typing import List
from web3.types import Address
from enum import Enum, IntEnum

class Side(IntEnum):
    BUY = 0
    SELL = 1

class SignatureVersion(IntEnum):
    EIP712 = 0
    PERSONAL_SIGN = 1
    ETH_SIGN = 2
    EIP1271 = 3

class Fee(BaseModel):
    rate: int
    recipient: Address

class Order(BaseModel):
    trader: Address
    side: Side
    matchingPolicy: Address
    collection: Address
    tokenId: int
    amount: int
    paymentToken: Address
    price: int
    listingTime: int
    expirationTime: int
    fees: List[Fee]
    salt: int
    extraParams: bytes

class Input(BaseModel):
    order: Order
    v: int
    r: bytes
    s: bytes
    extraSignature: bytes
    signatureVersion: SignatureVersion
    blockNumber: int

class Execution(BaseModel):
    sell: Input
    buy: Input
