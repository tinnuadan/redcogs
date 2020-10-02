import typing
from .backend.interface import BackendInterface, SearchKey as ISearchKey
from .shop import Shop

# create an alias, so that we can import shopmanager.SearchKey and don't have to know about the interface
SearchKey = ISearchKey

class ShopManager(BackendInterface):
  def __init__(self, backend: BackendInterface):
    super().__init__()
    self._backend = backend

  def getShop(self, guild_id: int, id: typing.Union[int, str]):
    return self._backend.getShop(guild_id, id)

  def addShop(self, guild_id: int, shop: Shop) -> typing.Union[None, Shop]:
    return self._backend.addShop(guild_id, shop)

  def removeShop(self, guild_id: int, shop: Shop) -> bool:
    return self._backend.removeShop(guild_id, shop)

  def updateShop(self, guild_id: int, currentShop: Shop, newShop: Shop) -> typing.Union[None, Shop]:
    return self._backend.updateShop(guild_id, currentShop, newShop)

  def searchShop(self, guild_id: int, needle: str, where: SearchKey) -> typing.Union[None, Shop]:
    return self._backend.searchShop(guild_id, needle, where)

  def getItem(self, guild_id: int, id):
    return self._backend.getItem(guild_id, id)

  def updateItem(self, guild_id: int, currentItem, newItem):
    return self._backend.updateItem(guild_id, currentItem, newItem)

  def list(self, guild_id: int) -> typing.List:
    return self._backend.list(guild_id)
