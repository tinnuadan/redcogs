import sqlite3
import typing
import copy
from .interface import BackendInterface, SearchKey
from ..shop import Shop
from ..item import Item
from ..coordinates import Coordinates, World
from ..logging import getLogger

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
  return world.value

def _convert_world(id):
  return World(int(id))
  

sqlite3.register_adapter(Coordinates, _adapt_coordinates)
sqlite3.register_adapter(World, _adapt_world)
sqlite3.register_converter("coordinates", _convert_coordinates)
sqlite3.register_converter("world", _convert_world)


class SqliteBackend(BackendInterface):
  _SCHEME = ["""CREATE TABLE IF NOT EXISTS `items` (
`item_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
`guild_id` INTEGER NOT NULL,
`shop_id` INTEGER NOT NULL,
`name` TEXT,
`price` TEXT
);""","""CREATE TABLE IF NOT EXISTS `shops` (
`shop_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
`guild_id` INTEGER NOT NULL,
`name` TEXT,
`owner` TEXT,
`coordinates` `coordinates` TEXT,
`world` `world` INTEGER,
`post` TEXT,
`status` TEXT
);"""]
  _TBL_ITEMS: str = "items"
  _TBL_SHOPS: str = "shops"


  def __init__(self, filename: str = ":memory:"):
    super().__init__()
    if filename == ":memory:":
      getLogger().warning("The database is set to be kept in memory")
    self._db: sqlite3.Connection = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
    self._db.row_factory = _dict_factory
    self._c: sqlite3.Cursor = self._db.cursor()
    for statement in SqliteBackend._SCHEME:
      self._c.execute(statement)
    self._db.commit()

  def _row2shop(self, row: typing.List) -> Shop:
    owner = row['owner'].split(",") if row['owner'] else []
    shop = Shop(row['name'], owner, [], row['coordinates'], row['post'], row['shop_id'])
    shop.coords.world = World(row['world'])
    return shop

  def _row2item(self, row: typing.List, shop: Shop = None) -> Item:
    return Item(row['name'], row['price'], row['item_id'], shop)

  def list(self, guild_id: int): #don't fetch shops, only id and name
    cur: sqlite3.Cursor = self._c
    cur.execute("SELECT * FROM `shops` WHERE `guild_id`=:guild_id ORDER BY `name` ASC", {"guild_id": guild_id})
    shops = {}
    while True:
      row = cur.fetchone()
      if not row:
        break
      shops[row['shop_id']] = row['name']
    return shops


  def getShop(self, guild_id: int, id: typing.Union[int, str]):
    cur: sqlite3.Cursor = self._c
    try:
      id = int(id)
    except ValueError:
      pass

    if isinstance(id, int):
      cur.execute("SELECT * FROM `shops` WHERE `guild_id`=:guild_id AND `shop_id`=:id", {"guild_id": guild_id, "id": id})
    else:
      cur.execute("SELECT * FROM `shops` WHERE `guild_id`=:guild_id AND `name` LIKE :name", {"guild_id": guild_id, "name": id})
    row = cur.fetchone()
    if not row:
      getLogger().error(f"The shop with the id {id} was not found")
      return None
    shop = self._row2shop(row)
    cur.execute("SELECT * FROM `items` WHERE `shop_id`=:id ORDER BY `name` ASC", {"id": shop.id})
    while True:
      row = cur.fetchone()
      if not row:
        break
      item = self._row2item(row, shop)
      shop.items.append(item)
    return shop
    
  def addShop(self, guild_id: int, shop: Shop):
    getLogger().info(f"Add new shop")
    cur: sqlite3.Cursor = self._c
    owner = ",".join(shop.owner) if shop.owner != None else None
    cur.execute("""INSERT INTO `shops`
      (`guild_id`, `name`,`owner`,`coordinates`,`world`,`post`,`status`)
      VALUES(?,?,?,?,?,?,'active')""", (guild_id, shop.name, owner, shop.coords, shop.coords.world, shop.post))
    shop.id = cur.lastrowid

    items: typing.List = []
    for itm in shop.items:
      items.append((guild_id, shop.id, itm.name, itm.price))
    if len(items) > 0:
      cur.executemany("""INSERT INTO `items` (`guild_id`,`shop_id`,`name`,`price`) VALUES(?,?,?,?)""", items)
    self._db.commit()
    return self.getShop(shop.id)

  def updateShop(self, guild_id: int, oldValue: Shop, newValue: Shop):
    if oldValue.id <= 0:
      getLogger().error(f"The shop id {oldValue.id} is not valid")
      return None
    if self.getShop(oldValue.id) == None:
      getLogger().error(f"The shop id {oldValue.id} was not found")
      return None
    if oldValue.isSame(newValue):
      getLogger().info(f"Nothing changed")
      return oldValue
    getLogger().info(f"Updating shop#id{oldValue.id}")

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
      cur.execute("DELETE FROM `items` WHERE `item_id`=?", (itm.id,))
    # update existing
    for itm in existingItems:
      cur.execute("UPDATE `items` SET `name`=?, `price`=? WHERE `item_id`=?", (itm.name, itm.price, itm.id))
    # insert new
    items: typing.List[Item] = []
    for itm in newItems:
      items.append((guild_id, oldValue.id, itm.name, itm.price))
    if len(items) > 0:
      cur.executemany("""INSERT INTO `items` (`guild_id`,`shop_id`,`name`,`price`) VALUES(?,?,?,?)""", items)
    self._db.commit()
    return self.getShop(oldValue.id)

  def removeShop(self, guild_id: int, shop) -> bool:
    todelete = self.getShop(shop.id)
    if todelete == None:
      getLogger().warning(f"Unable to delete the shop \"{shop.name}\" because it's id wasn't found")
      return False
    
    #remove items:
    cur: sqlite3.Cursor = self._c
    cur.execute("DELETE FROM `items` WHERE `shop_id`=?", (todelete.id,))
    cur.execute("DELETE FROM `shops` WHERE `shop_id`=?", (todelete.id,))
    self._db.commit()
    return True

  def getItem(self, guild_id: int, id):
    cur: sqlite3.Cursor = self._c
    cur.execute("SELECT * FROM `items` WHERE `item_id`=:id", {"id": id})
    row = cur.fetchone()
    if not row:
      getLogger().error(f"The item with the id {id} was not found")
      return None
    shop = self.getShop(int(row['shop_id']))
    return shop.getItem(int(id))

  def updateItem(self, guild_id: int, currentItem, newItem):
    cur: sqlite3.Cursor = self._c
    if currentItem.isSame(newItem):
      return True
    cur.execute("UPDATE `items` SET `name`=:name, `price`=:price WHERE `item_id`=:id", {"id": currentItem.id, 'name': newItem.name, 'price': newItem.price})
    self._db.commit()
    updated = self.getItem(currentItem.id)
    return updated.name == newItem.name and updated.price == newItem.price
  
  def searchShop(self, guild_id: int, needle, where) -> typing.List[Shop]:
    def _append_if_not_exists(l, id):
      if id in l:
          return
      l.append(id)
    ids = []
    res = []
    cur: sqlite3.Cursor = self._c
    # search for name
    if where == SearchKey.Name or where == SearchKey.Any:
      cur.execute("SELECT `shop_id` FROM `shops` WHERE `guild_id`=? AND `name` LIKE ? ORDER BY `name` ASC ", (guild_id, f"%{needle}%"))
      while True:
        row = cur.fetchone()
        if not row:
          break
        _append_if_not_exists(ids, row['shop_id'])
    # search for owner
    if where == SearchKey.Owner or where == SearchKey.Any:
      cur.execute("SELECT `shop_id` FROM `shops` ASC WHERE WHERE `guild_id`=? AND `owner` LIKE ? ORDER BY `name`", (guild_id, f"%{needle}%"))
      while True:
        row = cur.fetchone()
        if not row:
          break
        _append_if_not_exists(ids, row['shop_id'])
    # search for items
    if where == SearchKey.Items or where == SearchKey.Any:
      cur.execute("SELECT `shop_id` FROM `items` WHERE WHERE `guild_id`=? AND `name` LIKE ? ORDER BY `name`", (guild_id, f"%{needle}%"))
      while True:
        row = cur.fetchone()
        if not row:
          break
        _append_if_not_exists(ids, row['shop_id'])
    for id in ids:
      res.append(self.getShop(id))
    return res



    




