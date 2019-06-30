import json
from ..src.convert_units import converter
from ..src.convert_units import measurements

def load_helper():
  c = converter.ConversionData()
  result = []
  with open("testdata_ratio.json", "r") as f:
    data = f.read()
    measure: dict = json.loads(data)
    c.metric = measurements.loadMeasurement(measure["metric"], True)
    c.imperial = measurements.loadMeasurement(measure["imperial"], False)
    result.append(c)
  
  c = converter.ConversionData()
  with open("testdata_transform.json", "r") as f:
    data = f.read()
    measure: dict = json.loads(data)
    c.metric = measurements.loadMeasurement(measure["metric"], True)
    c.imperial = measurements.loadMeasurement(measure["imperial"], False)
    result.append(c)
  
  converter.conversionsData = result


def test_findMeasure():
  m: measurements.Measurement = None
  with open("testdata_ratio.json", "r") as f:
    data = f.read()
    measure: dict = json.loads(data)
    m = measurements.loadMeasurement(measure["imperial"], False)
  
  measure = converter.findMeasureForUnit("m/h", m)

  assert m != None
  assert converter.findMeasureForUnit("km/h", m) == None
  assert converter.findMeasureForUnit("kn", m) != None
  assert converter.findMeasureForUnit("mph", m) == measure
  
