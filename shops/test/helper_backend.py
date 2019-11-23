import typing
from ..src.backend.interface import BackendInterface, SearchKey
from ..src.shop import Shop

class HelperBackend(BackendInterface):
  def __init__(self):
    super().__init__()

  def addShop(self, shop: Shop) -> typing.Union[None, Shop]:
    return shop

  def removeShop(self, shop: Shop) -> typing.Union[None, Shop]:
    return shop

  def editShop(self, currentShop: Shop, newShop: Shop) -> typing.Union[None, Shop]:
    return newShop

  def searchShop(self, needle: str, where: SearchKey) -> typing.Union[None, Shop]:
    return None
