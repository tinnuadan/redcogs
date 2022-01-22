from sqlite3 import OperationalError
import pymysql
import enum
import uuid


class SyncResult(enum.Enum):
  DBNotSetup = enum.auto()
  NoDBConnection = enum.auto()
  DBError = enum.auto()
  Success = enum.auto()

class Sync:
  def __init__(self):
    self.server = None
    self.user = None
    self.password = None

  def link(self, discord_id: int, minecraft_id: uuid.UUID):
    if self.server == None or self.user == None or self.password == None:
      return SyncResult.DBNotSetup
    try:
      db = pymysql.connect(host=self.server,
                user=self.user,
                password=self.password,
                database="patreon")
      if not db:
        return SyncResult.NoDBConnection
      with db:
        cur = db.cursor()
        sql = f"""INSERT INTO `minecraft2discord`
            (`minecraft_uuid`, `discord_id`)
            VALUES('{str(minecraft_id)}','{discord_id}')"""
        try:
          cur.execute(sql)
          db.commit()
        except pymysql.err.Error as e:
          print(e)
          # Rollback in case there is any error
          db.rollback()
          return SyncResult.DBError
        return SyncResult.Success
    except pymysql.err.OperationalError as e:
      print(e)
      return SyncResult.DBError

  def unlink(self, discord_id: int, minecraft_id: uuid.UUID):
    if self.server == None or self.user == None or self.password == None:
      return SyncResult.DBNotSetup
    try:
      db = pymysql.connect(host=self.server,
                user=self.user,
                password=self.password,
                database="patreon")
      if not db:
        return SyncResult.NoDBConnection
      with db:
        cur = db.cursor()
        sql = f"""DELETE FROM `minecraft2discord` WHERE `minecraft_uuid`='{str(minecraft_id)}' AND `discord_id`='{discord_id}'"""
        try:
          cur.execute(sql)
          db.commit()
        except pymysql.err.Error as e:
          print(e)
          # Rollback in case there is any error
          db.rollback()
          return SyncResult.DBError
        return SyncResult.Success
    except pymysql.err.OperationalError as e:
      print(e)
      return SyncResult.DBError


if __name__ == "__main__":
  s = Sync()
  s.server = "localhost"
  s.user = "patreon"
  s.password = "patreon"
  print(s.unlink(1, uuid.UUID("12345678-1234-5678-1234-567812345678")))