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
    gt = gt + ("?" if i[0]==None else str(i[0])) + ","
    gt = gt + ("?" if i[1]==None else str(i[1])) + ","
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
