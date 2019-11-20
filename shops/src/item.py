from typing import List, Dict

class Item:
  def __init__(self, name: str = "", price: float = 0., id: int = -1):
    self._id = id
    self._name = name
    self._price = price
