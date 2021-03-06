from ..src.backend.sqlitebackend import SqliteBackend
from ..src.backend.interface import SearchKey
from ..src.shop import Shop
from ..src.item import Item
from ..src.coordinates import Coordinates
import copy

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
  shop = Shop("Test Shop", ["bean"], [Item("Cod", "1 Diamond"), Item("Salmon", "1 Diamond")], Coordinates(19,64,10), "discord")
  shop = backend.addShop(shop) # update with the ids
  newValue = copy.deepcopy(shop)
  newValue.name = "Test Shop2"
  newValue.owner.append("luci")
  newValue.items[1].price = "2 Diamond" # price for salmon
  newValue.items[0] = Item("Steak", "1 Diamond") # replace cod
  updated = backend.updateShop(shop, newValue)
  assert updated.id == shop.id
  assert updated.name == "Test Shop2"
  assert len(updated.owner)==2 and updated.owner[0]=="bean" and updated.owner[1]=="luci"
  assert len(updated.items)==2
  assert len(list(filter(lambda x: x.name == "Cod", updated.items))) == 0
  assert len(list(filter(lambda x: x.name == "Steak", updated.items))) == 1
  assert list(filter(lambda x: x.name == "Salmon", updated.items))[0].id == list(filter(lambda x: x.name == "Salmon", shop.items))[0].id
  assert list(filter(lambda x: x.name == "Steak", updated.items))[0].id != list(filter(lambda x: x.name == "Cod", shop.items))[0].id


def test_remove():
  backend = getBackend()
  shop = Shop("Test Shop", ["bean"], [], Coordinates(19,64,10), "discord")
  inserted: Shop = backend.addShop(shop)
  persistend = backend.getShop(inserted.id)

  id = inserted.id
  assert inserted.id != 0
  assert inserted.name == shop.name
  assert persistend != None
  assert persistend.isSame(inserted) == True

  assert backend.removeShop(inserted)
  assert backend.getShop(id) == None


def test_item():
  backend = SqliteBackend()
  shop = Shop("Test Shop", ["bean"], [Item("Cod", "1 Diamond"), Item("Salmon", "1 Diamond")], Coordinates(19,64,10), "discord")
  shop = backend.addShop(shop)

  assert len(shop.items) == 2
  item = backend.getItem(1)
  assert item != None
  assert item.id == 1
  assert item.name == "Cod"
  assert item.price == "1 Diamond"
  
  newItem = copy.deepcopy(item)
  newItem.name = "Chicken"
  newItem.price = "2 Diamonds"
  assert backend.updateItem(item, newItem)
  item = backend.getItem(1)
  assert item != None
  assert item.id == 1
  assert item.name == "Chicken"
  assert item.price == "2 Diamonds"





