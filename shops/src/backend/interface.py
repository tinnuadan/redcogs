import typing
import enum
from ...src.shop import Shop
from ...src.item import Item

class SearchKey(enum.Enum):
  Any = 1
  Name = 2
  Owner = 3
  Items = 4

class BackendInterface:
  def __init__(self):
    super().__init__()

  def getShop(self, id: typing.Union[int, str]) -> typing.Union[None, Shop]:
    return None

  def addShop(self, shop: Shop) -> typing.Union[None, Shop]:
    return None

  def removeShop(self, shop: Shop) -> bool:
    return False

  def updateShop(self, currentShop: Shop, newShop: Shop) -> typing.Union[None, Shop]:
    return None

  def searchShop(self, needle: str, where: SearchKey) -> typing.List[Shop]:
    return None

  def getItem(self, id: int) -> typing.Union[None, Item]:
    return None

  def updateItem(self, currentItem: Item, newItem: Item) -> bool:
    return False

  def list(self) -> typing.List:
    return []