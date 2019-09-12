import json
from typing import Dict, List


class Measure():
  """ A single measure (e.g. kg). Contains the conversion to the anchor, the unit, name, aliases and the parent Measurement collection"""

  def __init__(self, parent):
    self.unit: str = ""
    self.aliases: List = []
    self.name: str = ""
    self.to_anchor: float = 1
    self.anchor_shift: float = 0
    self.parent: Measurement = parent

  def __str__(self):
    aliases = list(self.aliases)
    aliases.remove(self.name)
    res = "%s (%s). Also known as %s. To anchor: %.2f. Anchor shift: %.2f" %(self.unit, self.name, ", ".join(aliases), self.to_anchor, self.anchor_shift)
    return res


class Anchor():
  """ Holds which Measure is used as the anchor of a Measurement """
  def __init__(self):
    self.measure: Measure = None
    self.ratio: float = 1
    self.transform = None


class Measurement():
  """ Holds a collection of measures (metric or imperial), which have a common anchor they can be converted to """

  def __init__(self, name: str):
    self.name: str = name
    self.anchor: Anchor = Anchor()
    self.measures: List = []
    self.is_metric: bool = False

  def hasUnit(self, unit: str):
    for m in self.measures:
      if m.unit == unit:
        return True
    return False

def autoConvertFraction(frac: any):
  if isinstance(frac, str):
    tmp = frac.split("/") #ratio
    return float(tmp[0]) / float(tmp[1])
  else:
    return frac

def loadMeasurement(name: str, definition: Dict, is_metric: bool):
  result: Measurement = Measurement(name)
  result.is_metric = is_metric
  anchor: Anchor = result.anchor
  anchor_unit: str = None
  for kt, vt in definition.items():
    k: str = kt
    v: Dict = vt
    if k == "_anchor":
      anchor_unit = v["unit"]
      if "transform" in v.keys():
        anchor.transform = eval("lambda x: %s" % v["transform"])
      else:
        anchor.ratio = autoConvertFraction(v["ratio"])
    elif k[0] != "_":
      m: Measure = Measure(result)
      m.unit = k
      if "aliases" in v.keys():
        m.aliases = v["aliases"]
      m.aliases.append(v["name"]["singular"])
      m.aliases.append(v["name"]["plural"])
      m.name = v["name"]["singular"]
      m.to_anchor = autoConvertFraction(v["to_anchor"])
      result.measures.append(m)
  for m in result.measures:
    if m.unit == anchor_unit:
      anchor.measure = m
      break
  if not result.anchor.measure:
    raise Exception("Basic measure for anchor not found")
  return result

  





