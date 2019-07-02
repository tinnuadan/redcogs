
import json
import os
from typing import Dict, List
from .measurements import loadMeasurement, Measurement, Measure


class ConversionData:
  def __init__(self):
    self.metric: Measurement = None
    self.imperial: Measurement = None

class ConversionResult:
  def __init__(self, value, measure):
    self.value: float = value
    self.measure: Measure = measure

  def __str__(self):
    return "%.2f %s" % (self.value, self.measure.unit)

  def toBest(self):
    """  Looks through every possibility for the 'best' available unit.
    i.e. Where the value has the fewest numbers before the decimal point,
    but is still higher than 1."""
    measurement: Measurement = self.measure.parent
    if not measurement.hasUnit(self.measure.unit):
      raise Exception("Measurement does not include unit %s" % self.measure.unit)
    
    result: Dict = {'nbd': 1e6, 'measurement': self.measure}

    value = self.value
    if self.measure != measurement.anchor.measure:
      value = value * self.measure.to_anchor

    for m in measurement.measures:
      v: float = abs(value / m.to_anchor)
      if v > 1:
        tmp = ("%.2f" % v).split(".")
        if len(tmp[0]) < result['nbd']:
          result['nbd'] = len(tmp[0])
          result['measurement'] = m
    
    return ConversionResult( value / result['measurement'].to_anchor, result['measurement'])


class Conversion:
  def __init__(self, conversionData: ConversionData, base_measure: Measure, isBaseMetric: bool):
    self.conversion: ConversionData = conversionData
    self.base_measure: Measure = base_measure
    self.is_base_metric: bool = isBaseMetric

  def cfrom(self):
    if not self.conversion:
      raise Exception("No conversion set")
    return self.conversion.metric if self.is_base_metric else self.conversion.imperial

  def cto(self):
    if not self.conversion:
      raise Exception("No conversion set")
    return self.conversion.metric if not self.is_base_metric else self.conversion.imperial
  
  def convert(self, value: float):
    print("Converting %s to %s" % (self.base_measure.unit, self.cto().anchor.measure.unit))
    result: float = 0

    result = value * self.base_measure.to_anchor - self.base_measure.anchor_shift

    to: Measurement = self.cto()
    fr: Measurement = self.cfrom()

    if(fr.anchor.transform != None):
      result = fr.anchor.transform(result)
    else:
      result = result * fr.anchor.ratio

    result_measure: Measure = to.anchor.measure
    return ConversionResult(result, result_measure)

  def convertTo(self, value: float, to: Measure):
    print("Converting %s to %s" % (self.base_measure.unit, to.unit))
    result: float = 0

    #parents must be the same
    if self.base_measure.parent != to.parent:
      raise Exception("Parents must be the same")
  
    # to anchor
    result = value * self.base_measure.to_anchor - self.base_measure.anchor_shift
    # to the new value
    result = (result + to.anchor_shift) / to.to_anchor

    return ConversionResult(result, to)



conversionsData: List = []

def loadConversionsData():
  global conversionsData
  result: List = []
  available: List = ["area", "length", "mass", "speed", "temperature", "volume"]
  base_path = os.path.split(os.path.realpath(__file__))
  for v in available:
    c = ConversionData()
    with open("%s/definitions/%s.json" % (base_path, v), "r") as f:
      print("Loading %s" % v)
      data = f.read()
      measure: dict = json.loads(data)
      c.metric = loadMeasurement(v, measure["metric"], True)
      c.imperial = loadMeasurement(v, measure["imperial"], False)
      result.append(c)
  conversionsData = result



def findMeasureForUnit(unit: str, measurement: Measurement):
  for m in measurement.measures:
    measure: Measure = m
    aliases = list(map(lambda x: x.lower(), measure.aliases))
    if measure.unit == unit or unit in aliases:
      return m
  return None

def findConversion(unit: str):
  global conversionsData
  result: Conversion = None
  for c in conversionsData:
    m: Measure = findMeasureForUnit(unit, c.metric)
    if m:
      result = Conversion(c, m, True)
      break
    if result != None:
      break
    m = findMeasureForUnit(unit, c.imperial)
    if m:
      result = Conversion(c, m, False)
      break
    if result != None:
      break
  return result

