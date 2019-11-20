from typing import List, Dict
from .item import Item
from .coordinates import Coordinates

class Shop:
  def __init__(self, name: str = "", owner: List = [], items: Dict = {}, coords: Coordinates = Coordinates(), post: str = "", id: int = -1):
    super().__init__()
    self._id = id
    self._name = name
    self._owner = owner
    self._items = items
    self._coords = coords
    self._post = post

  def getDynmapUrl(self):
    return "http://patreon.docm77.de:8123/?worldname=DocsWorldTour&mapname=flat&zoom=5&x%s&&z=%s" % (self._coords._x, self._coords._z)