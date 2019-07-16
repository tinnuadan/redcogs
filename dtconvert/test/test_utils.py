from ..src import utils
import datetime
from .helpers import getTimezones


def testToUnixTime():
  tzinfo = getTimezones().getTzInfo("CEST")
  dt = datetime.datetime(2019, 7, 14, 12, 0,0, 0, tzinfo)
  assert utils.toUnixTime(dt) == 1563098400