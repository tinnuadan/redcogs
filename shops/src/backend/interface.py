import typing
import enum
from ...src.shop import Shop

class SearchKey(enum.Enum):
  Any = 1
  Name = 2
  Owner = 3
  Items = 4

class BackendInterface:
  def __init__(self):
    super().__init__()

  def getShop(self, id: int) -> typing.Union[None, Shop]:
    return None

  def addShop(self, shop: Shop) -> typing.Union[None, Shop]:
    return None

  def removeShop(self, shop: Shop) -> bool:
    return False

  def updateShop(self, currentShop: Shop, newShop: Shop) -> typing.Union[None, Shop]:
    return None

  def searchShop(self, needle: str, where: SearchKey) -> typing.Union[None, Shop]:
    return None

  