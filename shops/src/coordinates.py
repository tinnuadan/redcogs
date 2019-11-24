class Coordinates:
  def __init__(self, x: int = None, y: int = None, z: int = None):
    super().__init__()
    self.x = x
    self.y = y
    self.z = z

  def isValid(self):
    return self._x != None and self._z != None
  
  def getDynmapUrl(self):
    if not self.isValid:
      return None
    return "http://patreon.docm77.de:8123/?worldname=DocsWorldTour&mapname=flat&zoom=5&x%s&&z=%s" % (self.x, self.z)

  def __str__(self):
    xyz = list(map(lambda v: "?" if v == None else str(v), [self.x, self.y, self.z]))
    return ",".join(xyz)

  @staticmethod
  def fromString(representation: str):
    tmp = list(map(lambda v: v.strip(), str.strip().split(",")))
    tmp = list(map(lambda v: None if v=="?" else int(v), tmp))
    return Coordinates(tmp[0], tmp[1], tmp[2])