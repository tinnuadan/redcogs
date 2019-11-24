from typing import List, Dict
from .item import Item
from .coordinates import Coordinates

class Shop:
  def __init__(self, name: str = "", owner: List = None, items: Dict = None, coords: Coordinates = Coordinates(), post: str = None, id: int = -1):
    super().__init__()
    self.id = id
    self.name = name
    self.owner: List = owner
    self.items: Dict = items
    self.coords = coords
    self.post = post

  def getDynmapUrl(self):
    return self._coords.getDynmapUrl()