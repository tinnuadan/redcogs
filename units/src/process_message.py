import json
import os
import re
from typing import List, Dict
from .convert_units import converter
from .convert_units import measurements
from .error import Error

class _MatchToProcess:
  def __init__(self, match, conversion: converter.Conversion):
    self.match: re.Match = match
    self.conversion: converter.Conversion = conversion
  
  def convert(self):
    return self.conversion.convert(self.value())
    
  def convertTo(self, to: measurements.Measure):
    return self.conversion.convertTo(self.value(), to)

  def value(self):
    value: float = 0
    tmp: str = self.match.group(1)
    if ',' in tmp:
      tmp = tmp.replace(',', '')
    if '\'' in tmp:
      tmp = tmp.replace('\'', '')
    value = float(tmp)
    return value

class _ToConvert:
  def __init__(self, matchToProces: _MatchToProcess, composedMTP: _MatchToProcess = None, separator: str = None):
    self.matchToProcess: _MatchToProcess = matchToProces
    self.composedMTP: _MatchToProcess = composedMTP
    self.separator: str = separator
    self.is_composed: bool = composedMTP != None
    self.override_to_conversion: converter.Conversion = None

class ConversionResult:
  def __init__(self, orig, conv):
    self.orig: str = orig
    self.conv: str = conv

class MessageProcessor:
  _re: re.Pattern = re.compile(r'(-?[\d,]+\.?\d*)\s?([\w\/\'"]+)')
  _reTo: re.Pattern = re.compile(r'to\s([\w\/\'"]+)$')
  _special: Dict = None

  def __init__(self):
    if MessageProcessor._special == None:
      base_path = os.path.split(os.path.realpath(__file__))[0]
      bollocks = os.path.join(base_path, "convert_units", "definitions", "bollocks.json")
      with open(bollocks, "r") as f:
        data = f.read()
        special: dict = json.loads(data)
        MessageProcessor._special = dict(map(lambda kv: (kv[0].lower(), kv[1]), special.items()))
    
  
  def processMessage(self, msg: str):
    # find all matches
    sp = self._findSpecial(msg)
    if(sp != None):
      return sp
    matches = self._findMatches(msg)
    composed = self._findComposed(matches, msg)
    composed = self._findTo(composed, msg)
    converted = self._processToConvert(composed)
    return converted

  def _findSpecial(self, msg: str):
    special: Dict = MessageProcessor._special
    m = msg.lower().strip()
    if m in special.keys():
      return special[m]
    return None

  def _findMatches(self, msg: str):
    matches = []
    it = MessageProcessor._re.finditer(msg)
    for m in it:
      #search for conversion
      conversion = converter.findConversion(m.group(2))
      if conversion:
        matches.append(_MatchToProcess(m, conversion))
    return matches

  def _findComposed(self, matches, msg):
    # find stuff like 5' 11"
    maxDiff = 3
    result: List = []
    skipNext = False

    for i in range(0, len(matches), 1):
      if skipNext: # Element already handled by composing it with the previous one
        skipNext = False
        continue

      cur: _MatchToProcess = matches[i]
      if i + 1 == len(matches): #we're already at the last element
        result.append(_ToConvert(cur))
        break
      next: _MatchToProcess = matches[i+1]
      diff = next.match.start() - cur.match.end()
      

      curConv: converter.Conversion = cur.conversion
      nextConv: converter.Conversion = next.conversion

      # if the same conversion classes are used and both matches are not far apart
      if curConv.is_base_metric == nextConv.is_base_metric and curConv.conversion.metric == nextConv.conversion.metric and diff <= maxDiff:
        separator: str = msg[cur.match.end() : next.match.start()]
        if len(separator.strip()) == 0: # if there are only whitespaces between the current and the next element
          # store the composed result
          result.append(_ToConvert(cur, next, separator))
          # skip one (i.e. the next) element
          skipNext = True
      else:
        result.append(_ToConvert(cur))
    return result

  def _findTo(self, toconvert, msg):
    # find 'val unit to unit'
    if len(toconvert) == 1: # only works for exaclty one conversion
      curelement: _ToConvert = toconvert[0]
      mtp: _MatchToProcess = curelement.matchToProcess if not curelement.is_composed else curelement.composedMTP
      substr: str = msg[mtp.match.end():].strip()
      m = self._reTo.match(substr) # if we match "to <unit>" at the end of the string
      if m:
        conversion = converter.findConversion(m.group(1)) # and have a valid conversion
        if conversion:
          origConv = curelement.matchToProcess.conversion
          if origConv.conversion.metric == conversion.conversion.metric:
            curelement.override_to_conversion = conversion
            return [curelement] # return the new list
          else:
            unit_from = origConv.base_measure.name
            unit_to = conversion.base_measure.name
            raise Error(f"Unable to convert from {unit_from.lower()} to {unit_to.lower()}")
    return toconvert

      
  def _processToConvert(self, matchToProcess):
    toReplace: List = []
    for tmp in matchToProcess:
      toConv: _ToConvert = tmp

      val = toConv.matchToProcess.value()

      if toConv.is_composed:
        val += toConv.composedMTP.convertTo(toConv.matchToProcess.conversion.base_measure).value

      result: converter.ConversionResult = None
      result = toConv.matchToProcess.conversion.convert(val)
      orig: str = str( converter.ConversionResult(val, toConv.matchToProcess.conversion.base_measure) )

      if toConv.override_to_conversion != None:
        print("forced conversion")
        
        if toConv.override_to_conversion.base_measure.parent == toConv.matchToProcess.conversion.base_measure.parent:
          # if the parents are the same (i.e. imperial -> imperial or metric -> metric)
          result = toConv.matchToProcess.conversion.convertTo(val, toConv.override_to_conversion.base_measure)
        else:
          # otherwise we convert first from imperial to metric or vice versa
          # (which we already did implicitly)
          
          # take the forced conversion
          conv: converter.Conversion = toConv.override_to_conversion
          # we take the base_measure of the forced conversion
          to_measure: measurements.Measure = conv.base_measure
          # and replace it in the class with the measure of the conversion result
          conv.base_measure = result.measure
          # and convert the whole thing
          result = conv.convertTo(result.value, to_measure)
      elif toConv.matchToProcess.conversion.conversion.convertToBest:
        result = result.toBest()

      conv: str = str(result)
      toReplace.append(ConversionResult(orig, conv))
    return toReplace
