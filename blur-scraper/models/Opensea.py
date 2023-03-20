from pydantic import BaseModel
from typing import List
from enum import Enum, IntEnum
from web3.types import Address

class ItemType(IntEnum):
    NATIVE = 0
    ERC20 = 1
    ERC721 = 2
    ERC1155 = 3
    ERC721_WITH_CRITERIA = 4
    ERC1155_WITH_CRITERIA = 5

class OrderType(IntEnum):
    FULL_OPEN = 0
    PARTIAL_OPEN = 1
    FULL_RESTRICTED = 2
    PARTIAL_RESTRICTED = 3
    CONTRACT = 4

class ConsiderationItem(BaseModel):
    itemType: ItemType
    token: Address
    identifierOrCriteria: int
    startAmount: int
    endAmount: int
    recipient: Address

class OrderComponents(BaseModel):
    offerer: Address
    zone: Address
    offer: List[ConsiderationItem]
    consideration: List[ConsiderationItem]
    orderType: OrderType
    startTime: int
    endTime: int
    zoneHash: bytes
    salt: int
    conduitKey: bytes
    counter: int
