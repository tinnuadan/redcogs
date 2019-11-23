import typing
from .backend.interface import BackendInterface, SearchKey as ISearchKey
from .shop import Shop

SearchKey = ISearchKey

class ShopManager:
  def __init__(self, backend: BackendInterface):
    super().__init__()
    self._backend = backend

  def addShop(self, shop: Shop) -> typing.Union[None, Shop]:
    return self._backend.addShop(shop)

  def removeShop(self, shop: Shop) -> typing.Union[None, Shop]:
    return self._backend.removeShop(shop)

  def editShop(self, currentShop: Shop, newShop: Shop) -> typing.Union[None, Shop]:
    return self._backend.editShop(currentShop, newShop)

  def searchShop(self, needle: str, where: SearchKey) -> typing.Union[None, Shop]:
    return self._backend.searchShop(needle, where)
