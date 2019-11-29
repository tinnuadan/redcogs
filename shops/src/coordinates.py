import enum

class World(enum.Enum):
  Overworld = 1
  Nether = 2
  End = 3

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
    return "http://patreon.docm77.de:8123/?worldname=DocsWorldTour&mapname=flat&zoom=5&x%s&&z=%s" % (self.x, self.z)

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