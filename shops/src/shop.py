from typing import List, Dict
from .item import Item
from .coordinates import Coordinates

class Shop:
  def __init__(self, name: str = "", owner: List = None, items: Dict = [], coords: Coordinates = Coordinates(), post: str = None, id: int = -1):
    super().__init__()
    self.id = id
    self.name = name
    self.owner: List = owner
    self.items: Dict = items
    self.coords = coords
    self.post = post

  def getDynmapUrl(self):
    return self.coords.getDynmapUrl()

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
