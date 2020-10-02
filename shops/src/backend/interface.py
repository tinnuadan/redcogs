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

  def getShop(self, guild_id: int, id: typing.Union[int, str]) -> typing.Union[None, Shop]:
    return None

  def addShop(self, guild_id: int, shop: Shop) -> typing.Union[None, Shop]:
    return None

  def removeShop(self, guild_id: int, shop: Shop) -> bool:
    return False

  def updateShop(self, guild_id: int, currentShop: Shop, newShop: Shop) -> typing.Union[None, Shop]:
    return None

  def searchShop(self, guild_id: int, needle: str, where: SearchKey) -> typing.List[Shop]:
    return None

  def getItem(self, guild_id: int, id: int) -> typing.Union[None, Item]:
    return None

  def updateItem(self, guild_id: int, currentItem: Item, newItem: Item) -> bool:
    return False

  def list(self, guild_id: int) -> typing.List:
    return []