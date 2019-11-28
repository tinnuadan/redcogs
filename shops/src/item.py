from typing import List, Dict

class Item:
  def __init__(self, name: str = "", price: str = None, id: int = -1, shop = None):
    self.id = id
    self.name = name
    self.price = price
    self.shop = shop

  def isSame(self, other):
    myself = self.__dict__
    theother = other.__dict__
    for key in myself:
      if myself[key] != theother[key]:
        return False
    return True
