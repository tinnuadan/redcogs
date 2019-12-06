import os
import json
import codecs
import typing

class Config:
  _config: typing.Dict = {}
  def __init(self):
    if len(Config._config) > 0:
      return
    configpath = os.path.join(os.path.realpath(__file__), "config.json")
    if not os.path.exists(configpath):
      raise Exception("No config found. Please rename config.json.example to config.json and adapt it to your needs")
    with codecs.open(configpath, "r", "utf-8") as f:
      data = f.read()
      Config._config = json.loads(data)

  @property
  def databaseuri(self):
    return Config._config['databaseuri']
      