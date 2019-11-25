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
  
def test_update():
  backend = getBackend()
  shop = Shop("Test Shop", ["bean"], [Item("Salmon", "1 Diamond"), Item("Cod", "1 Diamond")], Coordinates(19,64,10), "discord")
  shop = backend.addShop(shop) # update with the ids
  newValue = Shop("Test Shop2", ["bean","luci"], [Item("Salmon", "1 Diamond"), Item("Steak", "1 Diamond")], Coordinates(20,64,10), "discord")
  updated = backend.updateShop(shop, newValue)
  assert updated.id == shop.id
  assert updated.name == "Test Shop2"
  assert len(updated.owner)==2 and updated.owner[0]=="bean" and updated.owner[1]=="luci"
  assert len(updated.items)==2
  assert len(list(filter(lambda x: x.name == "Cod", updated.items))) == 0
  assert len(list(filter(lambda x: x.name == "Steak", updated.items))) == 1
