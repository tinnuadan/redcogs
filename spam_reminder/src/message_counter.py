from discord import Message, TextChannel
import time
import enum
import json

class MessageCounterResult(enum.Enum):
  WithinThreshold = 0
  OverThreshold = 1

class MessageCounter:
  def __init__(self, channel_watched, channel_out, msg_threshold, timespan):
    self.timestamps = []
    self.msg_threshold = msg_threshold
    self.timespan = timespan
    self.watched_channel = channel_watched
    self.channel_out = channel_out
    super().__init__()

  def new_msg(self):
    now = time.time()
    self.timestamps.append(now)
    while True:
      if self.timestamps[0] < now - self.timespan:
        del self.timestamps[0]
      else:
        break
    if len(self.timestamps) > self.msg_threshold:
      return MessageCounterResult.OverThreshold
    return MessageCounterResult.WithinThreshold
  
  def clear(self):
    self.timestamps.clear()

  def toJson(self):
    res = dict()
    res['msg_threshold'] = self.msg_threshold
    res['timespan'] = self.timespan
    res['watched_channel'] = self.watched_channel.id
    res['channel_out'] = self.channel_out.id
    return json.dumps(res)


# class MessageCounterMgr:
#   def __init__(self):
#     self.counters = dict() #TODO: load from config
#     self.counters[646341598623432715] = MessageCounter(646341598623432715, 2, 60)
#     super().__init__()

#   def new_msg(self, message: Message):
#     channel: TextChannel = message.channel
#     if channel.id in self.counters:
#       return self.counters[channel.id].new_msg()
#     return MessageCounterResult.WithinThreshold

#   def get_counter(self, channel):    
#     if channel.id in self.counters:
#       return self.counters[channel.id]
#     return None