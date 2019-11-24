import typing
from .backend.interface import BackendInterface, SearchKey as ISearchKey
from .shop import Shop

# create an alias, so that we can import shopmanager.SearchKey and don't have to know about the interface
SearchKey = ISearchKey

class ShopManager(BackendInterface):
  def __init__(self, backend: BackendInterface):
    super().__init__()
    self._backend = backend

  def getShop(self, id):
    return self._backend.getShop(id)

  def addShop(self, shop: Shop) -> typing.Union[None, Shop]:
    return self._backend.addShop(shop)

  def removeShop(self, shop: Shop) -> typing.Union[None, Shop]:
    return self._backend.removeShop(shop)

  def editShop(self, currentShop: Shop, newShop: Shop) -> typing.Union[None, Shop]:
    return self._backend.editShop(currentShop, newShop)

  def searchShop(self, needle: str, where: SearchKey) -> typing.Union[None, Shop]:
    return self._backend.searchShop(needle, where)
