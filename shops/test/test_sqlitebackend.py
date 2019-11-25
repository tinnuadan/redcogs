from ..src.backend.sqlitebackend import SqliteBackend
from ..src.backend.interface import SearchKey
from ..src.shop import Shop
from ..src.item import Item
from ..src.coordinates import Coordinates

_backend: SqliteBackend = None

def getBackend():
  global _backend
  if _backend == None:
    _backend = SqliteBackend()
  return _backend

def test_add():
  backend = getBackend()
  shop = Shop("Test Shop", ["bean"], [], Coordinates(19,64,10), "discord")
  inserted: Shop = backend.addShop(shop)
  persistend = backend.getShop(inserted.id)

  assert inserted.id != 0
  assert inserted.name == shop.name
  assert persistend != None
  assert persistend.isSame(inserted) == True
  

