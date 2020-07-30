from discord import Message, TextChannel
import time
import enum

class MessageCounterResult(enum.Enum):
  WithinThreshold = 0
  OverThreshold = 1

class MessageCounter:
  def __init__(self, channel_out, msg_threshold, timespan):
    self.timestamps = []
    self.msg_threshold = msg_threshold
    self.timespan = timespan
    super().__init__()

  def new_msg(self):
    now = time.time()
    self.timestamps.append(now)
    while True:
      if self.timestamps[0] < now - self.timespan:
        del self.timestamps[0]
    if len(self.timestamps) > self.msg_threshold:
      return MessageCounterResult.OverThreshold
    return MessageCounterResult.WithinThreshold
  
  def clear(self):
    self.timestamps.clear()


class MessageCounterMgr:
  def __init__(self):
    self.counters = dict() #TODO: load from config
    self.counters[646341598623432715] = MessageCounter(646341598623432715, 10, 60)
    super().__init__()

  def new_msg(self, message: Message):
    channel: TextChannel = message.channel
    channel_id = channel.id
    if channel.id in self.counters:
      return self.counters[channel.id].new_msg()
    return MessageCounterResult.WithinThreshold

  def get_counter(self, channel):    
    if channel.id in self.counters:
      return self.counters[channel.id]
    return None