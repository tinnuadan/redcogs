class Coordinates:
  def __init__(self, x: int = None, y: int = None, z: int = None):
    super().__init__()
    self._x = x
    self._y = y
    self._z = z

  def isValid(self):
    return self._x != None and self._z != None
  
  def getDynmapUrl(self):
    if not self.isValid:
      return None
    return "http://patreon.docm77.de:8123/?worldname=DocsWorldTour&mapname=flat&zoom=5&x%s&&z=%s" % (self._x, self._z)