from typing import List, Optional
from pydantic import BaseModel
import json


class Media(BaseModel):
    image: str
    thumbLg: str
    thumbSm: str
class CollectionItem(BaseModel):
    balanceNBT: str
    collectionAddress: str
    collectionId: str
    exchangeAddress: str
    exchangeId: str
    floorNBT: Optional[str]
    media: Optional[Media]
    name: Optional[str]
    networkId: int
    nftBalance: int
    nftVolumeAllTime: int
    offerNBT: Optional[str]
    volumeAllTimeNBT: str


class CollectionsData(BaseModel):
    items: Optional[List[CollectionItem]]
    cursor: Optional[str]

class CollectionsResponse(BaseModel):
    data: CollectionsData

def pydantic_encoder(obj):
    if isinstance(obj, BaseModel):
        return obj.dict()
    return obj
