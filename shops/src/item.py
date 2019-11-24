from typing import List, Dict

class Item:
  def __init__(self, name: str = "", price: str = None, id: int = -1):
    self.id = id
    self.name = name
    self.price = price
