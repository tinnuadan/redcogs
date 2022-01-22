import requests as req
import enum
import uuid
import json


class UUIDResult(enum.Enum):
  NotValid = enum.auto()
  NotFound = enum.auto()
  NetworkError = enum.auto()
  Success = enum.auto()

class MCUUID:
  def __init__(self) -> None:
    self.allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    
  def checkValidity(self, username: str):
    l = len(username)
    if l < 3 or l > 16:
      return False
    for c in username:
      if not c in self.allowed_chars:
        return False
    return True

  def getUUID(self, username):
    res = {"name": username, "id": None, "result": None}
    if not self.checkValidity(username):
      res["result"] = UUIDResult.NotValid
      return res
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    r = req.get(url)
    if r.status_code == 204:
      res["result"] = UUIDResult.NotFound
      return res
    if r.status_code != 200:
      res["result"] = UUIDResult.NetworkError
      return res
    tmp = json.loads(r.content)
    res["name"] = tmp["name"]
    res["id"] = uuid.UUID(tmp["id"])
    res["result"] = UUIDResult.Success
    return res
