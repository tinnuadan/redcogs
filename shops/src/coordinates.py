import enum

class World(enum.Enum):
  Overworld = 1
  Nether = 2
  End = 3

def World2Str(world: World) -> str:
  if world == World.Nether:
    return "Nether"
  if world == World.End:
    return "End"
  return "Overworld"

class Dynmap:
  _worlds = {
    World.Overworld: None,
    World.Nether: None,
    World.End: None
  }
  _server : None
  @staticmethod
  def getWorldName(world: World) -> str:
    return Dynmap._worlds[world]
  @staticmethod
  def setWorldName(world: World, name: str):
    Dynmap._worlds[world] = name
  @staticmethod
  def getServer() -> str:
    return Dynmap._server
  @staticmethod
  def setServer(server: str):
    Dynmap._server = server

class Coordinates:
  def __init__(self, x: int = None, y: int = None, z: int = None, world: World = World.Overworld):
    super().__init__()
    self.x = x
    self.y = y
    self.z = z
    self.world = world

  @property
  def isValid(self):
    return self.x != None and self.z != None
  
  def getDynmapUrl(self):
    if not self.isValid:
      return None
    server = Dynmap.getServer()
    if not server:
      return None
    world = Dynmap.getWorldName(self.world)
    if not world:
      return None
    return f"{server}/?worldname={world}&mapname=flat&zoom=5&x={self.x}&z={self.z}"

  def isSame(self, other):
    myself = self.__dict__
    theother = other.__dict__
    for key in myself:
      if myself[key] != theother[key]:
        return False
    return True

  def __str__(self):
    xyz = list(map(lambda v: "?" if v == None else str(v), [self.x, self.y, self.z]))
    return ", ".join(xyz)

  @staticmethod
  def fromString(representation: str):
    if representation == None:
      return Coordinates()
    tmp = list(map(lambda v: v.strip(), representation.strip().split(",")))
    tmp = list(map(lambda v: None if v=="?" else int(v), tmp))
    return Coordinates(tmp[0], tmp[1], tmp[2])