import json
from ..src.convert_units import measurements

def test_autofrac():
  assert measurements.autoConvertFraction(1.123) == 1.123
  assert measurements.autoConvertFraction("1/9") == 1/9

def test_loading():
  m: measurements.Measurement = None
  with open("testdata_ratio.json", "r") as f:
    data = f.read()
    measure: dict = json.loads(data)
    m = measurements.loadMeasurement("ratio", measure["metric"], True)
    
  assert m != None
  assert len(m.measures) == 2
  assert m.anchor.measure.unit == "km/h"
  assert m.anchor.ratio == 1/1.609344
  assert m.anchor.transform == None