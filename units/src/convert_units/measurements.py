import json
from typing import Dict, List


class Measure():  
  def __init__(self):
    self.unit: str = ""
    self.aliases: List = []
    self.name: str = ""
    self.to_anchor: float = 1
    self.anchor_shift: float = 0

  def __str__(self):
    aliases = self.aliases
    aliases.remove(self.name)
    res = "%s (%s). Also known as %s. To anchor: %.2f. Anchor shift: %.2f" %(self.unit, self.name, ", ".join(aliases), self.to_anchor, self.anchor_shift)
    return res


class Anchor():
  def __init__(self):
    self.measure: Measure = None
    self.ratio: float = 1
    self.transform = None


class Measurement():
  def __init__(self):
    self.anchor: Anchor = Anchor()
    self.measures: List = []
    self.is_metric: bool = False

  def hasUnit(self, unit: str):
    for m in self.measures:
      if m.unit == unit:
        return True
    return False


def loadMeasurement(definition: Dict, is_metric: bool):
  result: Measurement = Measurement()
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
        anchor.ratio = v["ratio"]
    elif k[0] != "_":
      m: Measure = Measure()
      m.unit = k
      if "aliases" in v.keys():
        m.aliases = v["aliases"]
      m.aliases.append(v["name"]["singular"])
      m.aliases.append(v["name"]["plural"])
      m.name = v["name"]["singular"]
      if isinstance(v["to_anchor"], str):
        tmp = v["to_anchor"].split("/") #ratio
        m.to_anchor = float(tmp[0]) / float(tmp[1])
      else:
        m.to_anchor = v["to_anchor"]
      result.measures.append(m)
  for m in result.measures:
    if m.unit == anchor_unit:
      anchor.measure = m
      break
  if not result.anchor.measure:
    raise Exception("Basic measure for anchor not found")
  return result

  





