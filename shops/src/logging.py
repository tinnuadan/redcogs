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

_SETUP = False
_logger = None

def getLogger():
  global _logger
  if _logger == None:
    return logging.getLogger()
  return _logger

def setupLogging(level, output_folder, prefix, max_files):
  global _SETUP
  global _logger
  if _SETUP:
    return
  _SETUP = True

  if _logger == None:
    _logger = logging.getLogger("tinnuadan.redcogs.shops")

  logger = _logger
  logger.propagate = False

  formatter = logging.Formatter("%(asctime)s %(levelname)s: %(module)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

  #clear everything  
  print(logger.handlers)
  for handler in logger.handlers:
    logger.removeHandler(handler)
  print(logger.handlers)
  time.sleep(0.02)

  # try to get the log level
  lvl = logging.INFO
  try:
    lvl = _LogLevel[level.upper()].value
  except KeyError:
    pass

  ch = logging.StreamHandler()
  ch.setLevel(lvl)
  ch.setFormatter(formatter)
  handlers = [ch]

  time.sleep(0.02)

  sep = os.path.sep
  if output_folder != None:
    if not os.path.exists(output_folder):
      try:
        os.mkdir(output_folder)
      except FileExistsError:
        pass
    # logging.getLogger(__name__).info(f"Adding file handler")       
    now = int(time.time())
    fn = f"{output_folder}{sep}{prefix}{now}.log"
    fh = logging.FileHandler(fn)
    fh.setLevel(lvl)
    fh.setFormatter(formatter)
    handlers.append(fh)

  logger.setLevel(lvl)
  print(handlers)
  for h in handlers:
    logger.addHandler(h)
  # logging.root.form

  # logging.basicConfig(level=lvl, format=format, handlers=handlers)
  print(logger.handlers)

  if output_folder != None:
    existing_files = glob.glob(f"{output_folder}{sep}{prefix}*.log")
    if len(existing_files) > max_files+1:
      existing_files = sorted(existing_files) #ascending -> oldest at front
      todelete = existing_files[0:max_files]
      for file in todelete:
        file = os.path.abspath(file)
        try:
          getLogger().info(f"Removing old log file {file}")    
          os.remove(file)
        except OSError as error: 
          print(error) 
          getLogger().error(f"Unable old log file {file}. Is the file write protected?")    

    


  

  

