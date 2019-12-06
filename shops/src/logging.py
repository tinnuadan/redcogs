import logging
import enum
import os
import glob
import time

class _LogLevel(enum.Enum): #stolen from the standard library
  CRITICAL = 50
  FATAL = CRITICAL
  ERROR = 40
  WARNING = 30
  WARN = WARNING
  INFO = 20
  DEBUG = 10
  NOTSET = 0


def setupLogging(level, output_folder, prefix, max_files):
  # try to get the log level
  lvl = logging.INFO
  try:
    lvl = _LogLevel[level.upper()]
  except KeyError:
    pass
  if output_folder == None:
    logging.basicConfig(level=lvl)
    return
  if not os.path.exists(output_folder):
    try:
      os.mkdir(output_folder)
    except FileExistsError:
      pass
  
  now = int(time.time())
  fn = f"{output_folder}/{prefix}{now}.log"
  logging.basicConfig(filename = fn, level=level)  
  
  existing_files = glob.glob(f"{output_folder}/{prefix}*.log")
  if len(existing_files) > max_files + 1: #plus one since we just created one
    existing_files = sorted(existing_files) #ascending -> oldest at front
    try:
      logging.getLogger(__name__).info(f"Removing old log file {existing_files[0]}")    
      os.remove(existing_files[0])
    except:
      logging.getLogger(__name__).error(f"Unable old log file {existing_files[0]}. Is the file write protected?")    

    


  

  

