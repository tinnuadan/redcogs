from typing import List, Dict, Union
from .item import Item
from .coordinates import Coordinates
from copy import deepcopy

class Shop:
  def __init__(self, name: str = "", owner: List = None, items: List = [], coords: Coordinates = Coordinates(), post: str = None, id: int = -1):
    super().__init__()
    self.id = id
    self.name = name
    self.owner: List = owner
    self.items: List = list(items)
    self.coords = coords
    self.post = post

  def clone(self):
    res = Shop()
    res.name = deepcopy(self.name)
    res.owner = list(self.owner)
    res.coords = deepcopy(self.coords)
    res.post = deepcopy(self.post)
    for itm in self.items:
      res.items.append(deepcopy(itm))
    return res

  def getDynmapUrl(self):
    return self.coords.getDynmapUrl()

  def hasItem(self, item: Item) -> bool:
    return self.getItem(item.id) != None

  def getItem(self, id: int) -> Union[None, Item]:
    for itm in self.items:
      if itm.id == id:
        return itm
    return None

  def isSame(self, other):
    simpleCheck = ['id','name','owner','post']
    myself = self.__dict__
    theother = other.__dict__
    for key in simpleCheck:
      if myself[key] != theother[key]:
        return False
    # if not self.coords.isSame(other.coords):
    #   return False
    if len(self.items) != len(other.items):
      return False
    for itemA, itemB in zip(self.items, other.items):
      if not itemA.isSame(itemB):
        return False
    return True
