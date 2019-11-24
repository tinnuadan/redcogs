import sqlite3
import logging
import typing
from .interface import BackendInterface
from ..shop import Shop
from ..item import Item
from ..coordinates import Coordinates

class SqliteBackend(BackendInterface):
  _SCHEME = """CREATE TABLE IF NOT EXISTS `items` (
`item_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
`shop_id` INTEGER NOT NULL,
`name` TEXT,
`price` TEXT
);

CREATE TABLE IF NOT EXISTS `shops` (
`shop_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
`name` TEXT,
`owner` TEXT,
`coordinates` TEXT,
`world` TEXT,
`post` TEXT
);"""
  _TBL_ITEMS: str = "items"
  _TBL_SHOPS: str = "shops"


  def __init__(self, filename: str = ":memory:"):
    super().__init__()
    if filename == ":memory:":
      logging.getLogger(__name__).warning("The database is set to be kept in memory")    
    self._db: sqlite3.Connection = sqlite3.connect(filename)
    self._c: sqlite3.Cursor = self._db.cursor()
    self._c.execute(_SCHEME)
    self._db.commit()

  def getShop(self, id: int):
    cur: sqlite3.Cursor = self._c
    cur.execute("SELECT * FROM `shops` WHERE `shop_id`=:id", {"id": id})
    row = cur.fetchone()
    if not row:
      return None
    owner = row['owner'].slit(",") if row['owner'] else None
    shop = Shop(row['name'], owner, None, Coordinates.fromString(row['coordinates']), row['post'], row['shop_id'])
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
      VALUES(?,?,?,?,?)""", (shop.name, owner, str(shop.coordinates), shop.world, shop.post))
    shop.id = cur.lastrowid

    items: typing.List[Item] = []
    for itm in shop.items:
      items.append((shop.id, itm.name, itm.price))
    
    if len(items) > 0:
      cur.executemany("""INSERT INTO `items` (`shop_id`,`name`,`price`) VALUES(?,?,?)""", items)
    
    return shop



