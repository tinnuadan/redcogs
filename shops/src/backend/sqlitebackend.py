import sqlite3
import logging
import typing
from .interface import BackendInterface
from ..shop import Shop
from ..item import Item
from ..coordinates import Coordinates, World

def _dict_factory(cursor: sqlite3.Cursor, row):
  d: typing.Dict = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def _adapt_coordinates(coord: Coordinates):
  return str(coord).encode('utf-8')

def _convert_coordinates(s: str):
  return Coordinates.fromString(s.decode('utf-8'))

def _adapt_world(world: World):
  return world.name.encode("utf-8")

def _convert_world(s: str):
  return World[s.decode('utf-8')]
  

sqlite3.register_adapter(Coordinates, _adapt_coordinates)
sqlite3.register_adapter(World, _adapt_world)
sqlite3.register_converter("coordinates", _convert_coordinates)
sqlite3.register_converter("world", _convert_world)


class SqliteBackend(BackendInterface):
  _SCHEME = ["""CREATE TABLE IF NOT EXISTS `items` (
`item_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
`shop_id` INTEGER NOT NULL,
`name` TEXT,
`price` TEXT
);""","""CREATE TABLE IF NOT EXISTS `shops` (
`shop_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
`name` TEXT,
`owner` TEXT,
`coordinates` `coordinates` TEXT,
`world` `world` TEXT,
`post` TEXT
);"""]
  _TBL_ITEMS: str = "items"
  _TBL_SHOPS: str = "shops"


  def __init__(self, filename: str = ":memory:"):
    super().__init__()
    if filename == ":memory:":
      logging.getLogger(__name__).warning("The database is set to be kept in memory")    
    self._db: sqlite3.Connection = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
    self._db.row_factory = _dict_factory
    self._c: sqlite3.Cursor = self._db.cursor()
    for statement in SqliteBackend._SCHEME:
      self._c.execute(statement)
    self._db.commit()

  def getShop(self, id: int):
    cur: sqlite3.Cursor = self._c
    cur.execute("SELECT * FROM `shops` WHERE `shop_id`=:id", {"id": id})
    row = cur.fetchone()
    if not row:
      logging.getLogger(__name__).error(f"The shop with the id {id} was not found")
      return None
    owner = row['owner'].split(",") if row['owner'] else None
    shop = Shop(row['name'], owner, [], row['coordinates'], row['post'], row['shop_id'])
    cur.execute("SELECT * FROM `items` WHERE `shop_id`=:id ORDER BY `name` ASC", {"id": shop.id})
    while True:
      row = cur.fetchone()
      if not row:
        break
      shop.items.append(Item(row['name'], row['price'], row['item_id']))
    return shop
    
  def addShop(self, shop: Shop):
    cur: sqlite3.Cursor = self._c
    owner = ",".join(shop.owner) if shop.owner != None else None
    cur.execute("""INSERT INTO `shops`
      (`name`,`owner`,`coordinates`,`world`,`post`)
      VALUES(?,?,?,?,?)""", (shop.name, owner, shop.coords, shop.coords.world, shop.post))
    shop.id = cur.lastrowid

    items: typing.List[Item] = []
    for itm in shop.items:
      items.append((shop.id, itm.name, itm.price))
    if len(items) > 0:
      cur.executemany("""INSERT INTO `items` (`shop_id`,`name`,`price`) VALUES(?,?,?)""", items)
    self._db.commit()
    return self.getShop(shop.id)

  def updateShop(self, oldValue: Shop, newValue: Shop):
    if oldValue.id <= 0:
      logging.getLogger(__name__).error(f"The shop id {oldValue.id} is not valid")
      return None
    if self.getShop(oldValue.id) == None:
      return None
    if oldValue.isSame(newValue):
      logging.getLogger(__name__).info(f"Nothing changed")
      return newValue

    shop = newValue
    cur: sqlite3.Cursor = self._c
    owner = ",".join(shop.owner) if shop.owner != None else None
    cur.execute("""UPDATE `shops` SET `name`=?, `owner`=?, `coordinates`=?, `world`=?, `post`=?
      WHERE `shop_id`=?""", (shop.name, owner, shop.coords, shop.coords.world, shop.post, oldValue.id))
    
    removedItems = list(filter(lambda x: not newValue.hasItem(x), oldValue.items)) # old has them, new not
    newItems = list(filter(lambda x: not oldValue.hasItem(x), newValue.items))     # new has them, old not
    existingItems = list(filter(lambda x: oldValue.hasItem(x), newValue.items))    # both have them

    # remove old
    for itm in removedItems:
      cur.execute("DELETE FROM `items` WHERE `item_id`=:id", (itm.id,))
    # update existing old
    for itm in removedItems:
      cur.execute("UPDATE `items` SET `name`=?, `price`=? WHERE `item_id`=?", (itm.name, itm.price, itm.id))
    # insert new
    items: typing.List[Item] = []
    for itm in newItems:
      items.append((oldValue.id, itm.name, itm.price))
    if len(items) > 0:
      cur.executemany("""INSERT INTO `items` (`shop_id`,`name`,`price`) VALUES(?,?,?)""", items)
    self._db.commit()
    return self.getShop(oldValue.id)

    




