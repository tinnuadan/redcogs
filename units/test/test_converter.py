import json
import math
from ..src.convert_units import converter
from ..src.convert_units import measurements

def load_helper():
  c = converter.ConversionData()
  result = []
  with open("testdata_ratio.json", "r") as f:
    data = f.read()
    measure: dict = json.loads(data)
    c.metric = measurements.loadMeasurement("ratio", measure["metric"], True)
    c.imperial = measurements.loadMeasurement("ratio", measure["imperial"], False)
    result.append(c)
  
  c = converter.ConversionData()
  with open("testdata_transform.json", "r") as f:
    data = f.read()
    measure: dict = json.loads(data)
    c.metric = measurements.loadMeasurement("transform", measure["metric"], True)
    c.imperial = measurements.loadMeasurement("transform", measure["imperial"], False)
    result.append(c)
  
  converter.conversionsData = result


def test_findMeasure():
  m: measurements.Measurement = None
  with open("testdata_ratio.json", "r") as f:
    data = f.read()
    measure: dict = json.loads(data)
    m = measurements.loadMeasurement("ratio", measure["imperial"], False)
  
  measure = converter.findMeasureForUnit("m/h", m)

  assert m != None
  assert converter.findMeasureForUnit("km/h", m) == None
  assert converter.findMeasureForUnit("kn", m) != None
  assert converter.findMeasureForUnit("mph", m) == measure
  
def test_findConversion():
  load_helper()
  
  assert converter.findConversion("kns") == None
  assert converter.findConversion("knot").base_measure.unit == "kn"
  assert converter.findConversion("knots").base_measure.unit == "kn"

def test_convertTo():
  load_helper()
  
  c = converter.findConversion("m/s")
  to = converter.findConversion("km/h")
  assert c != None
  assert to != None
  conv = c.convertTo(1, to.base_measure)
  assert conv.value == 3.6


def test_conversion_ratio():
  load_helper()

  c = converter.findConversion("kn")
  assert c != None
  conv = c.convert(10)
  assert conv.measure.unit == "km/h"
  assert math.isclose(conv.value, 18.52, abs_tol = 0.02)
  conv = conv.toBest()
  assert conv.measure.unit == "m/s"
  assert math.isclose(conv.value, 5.14444, abs_tol = 0.001)


def test_conversion_transform():
  load_helper()

  c = converter.findConversion("C")
  assert c != None
  conv = c.convert(10)
  assert conv.measure.unit == "F"
  assert math.isclose(conv.value, 50, abs_tol = 0.001)

  c = converter.findConversion("F")
  assert c != None
  conv = c.convert(50)
  assert conv.measure.unit == "C"
  assert math.isclose(conv.value, 10, abs_tol = 0.001)
