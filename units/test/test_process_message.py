import json
from ..src import process_message
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

def test_findMatches():
  load_helper()
  msg: str = "Lorem ipsum 10mph dolor sit amet, consectetur 29.1 km/h adipiscing elit 2,16 m/s. Cras accumsan nisi vitae elit suscipit 13.0, luctus pretium 2.3  kn est tincidunt."
  mp: process_message.MessageProcessor = process_message.MessageProcessor()
  matches = mp._findMatches(msg)

  assert len(matches) == 4
  assert matches[0].match.group(1) == "10"
  assert matches[0].match.group(2) == "mph"
  assert matches[1].match.group(1) == "29.1"
  assert matches[1].match.group(2) == "km/h"
  assert matches[2].match.group(1) == "2,16"
  assert matches[2].match.group(2) == "m/s"
  assert matches[3].match.group(1) == "2.3"
  assert matches[3].match.group(2) == "kn"

def test_findComposed():
  load_helper()
  msg: str = "Lorem ipsum 10mph 1 m/s dolor sit amet, consectetur 29.1 km/h 1 m/s adipiscing elit 2,16 m/s. Cras accumsan nisi vitae elit suscipit 13.0, luctus pretium 2.3  kn est tincidunt."
  mp: process_message.MessageProcessor = process_message.MessageProcessor()
  
  matches = mp._findMatches(msg)
  composed = mp._findComposed(matches, msg)

  assert len(matches) == 6
  assert len(composed) == 5
  assert composed[0].is_composed == False
  assert composed[1].is_composed == False
  assert composed[2].is_composed == True
  assert composed[3].is_composed == False
  assert composed[4].is_composed == False
  
  comp: process_message._ToConvert = composed[2]
  assert comp.separator == r' '
  assert comp.matchToProcess.match.group(0) == "29.1 km/h"
  assert comp.composedMTP.match.group(0) == "1 m/s"

def test_processToConvert():
  load_helper()
  msg: str = "Lorem ipsum 10mph 1 m/s dolor sit amet, consectetur 29.1 km/h 1 m/s adipiscing elit 2,16 m/s. Cras accumsan nisi vitae elit suscipit 13.0, luctus pretium 2.3  kn est tincidunt."
  mp: process_message.MessageProcessor = process_message.MessageProcessor()
  
  matches = mp._findMatches(msg)
  composed = mp._findComposed(matches, msg)
  converted = mp._processToConvert(composed)

  assert len(matches) == 6
  assert len(composed) == 5
  assert len(converted) == 5
  assert converted[0].orig == "10.00 mph"
  assert converted[0].conv == "16.09 km/h" 
  assert converted[1].orig == "1.00 m/s"
  assert converted[1].conv == "2.24 mph"
  assert converted[2].orig == "32.70 km/h"
  assert converted[2].conv == "20.32 mph"
  assert converted[3].orig == "2.16 m/s"
  assert converted[3].conv == "4.83 mph"
  assert converted[4].orig == "2.30 kn"
  assert converted[4].conv == "4.26 km/h"