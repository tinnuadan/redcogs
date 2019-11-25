from typing import List, Dict

class Item:
  def __init__(self, name: str = "", price: str = None, id: int = -1):
    self.id = id
    self.name = name
    self.price = price

  def isSame(self, other):
    myself = self.__dict__
    theother = other.__dict__
    for key in myself:
      if myself[key] != theother[key]:
        return False
    return True
