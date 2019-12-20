from ..src.shop import Shop
from ..src.item import Item
from ..src.coordinates import Coordinates, World

import itertools

def test_coordinates():
  values = [21, 37, 87, None, None, None]
  perm = itertools.permutations(values)
  for i in list(perm):
    coords = Coordinates(i[0], i[1], i[2])
    gt = ""
    gt = gt + ("?" if i[0]==None else str(i[0])) + ", "
    gt = gt + ("?" if i[1]==None else str(i[1])) + ", "
    gt = gt + ("?" if i[2]==None else str(i[2]))
    assert gt == str(coords)
  coords = Coordinates(10,11,12, World.Nether)
  assert coords.x == 10
  assert coords.y == 11
  assert coords.z == 12
  assert coords.world == World.Nether

def test_item():
  item = Item("test", "1 diamond")
  item2 = Item("test", "1 diamond")
  assert item.name == "test"
  assert item.price == "1 diamond"
  assert item.id == -1
  assert item.isSame(item2)
  item2.id = 10
  assert not item.isSame(item2)

def test_shop():
  shop = Shop("Test", ["Luci"], [Item("Potion", "1 Diamond")], Coordinates(10,11,12, World.Overworld), "discord", 4)
  shop2 = Shop("Test", ["Luci"], [Item("Potion", "1 Diamond")], Coordinates(10,11,12, World.Overworld), "discord", 4)
  assert shop.name == "Test"
  assert len(shop.owner) == 1 and shop.owner[0] == "Luci"
  assert len(shop.items) == 1 and shop.items[0].isSame(Item("Potion", "1 Diamond"))
  assert shop.coords.isSame(Coordinates(10,11,12, World.Overworld))
  assert shop.post == "discord"
  assert shop.id == 4
  assert shop.isSame(shop2)
  shop.owner[0] = "Bean"
  assert not shop.isSame(shop2)