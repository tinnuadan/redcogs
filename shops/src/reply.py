import enum
import discord

class MessageType(enum.Enum):
  Plain = enum.auto()
  Embed = enum.auto()
  Error = enum.auto()
  Confirmation = enum.auto()
  Success = enum.auto()


class Reply:
  def __init__(self, message: str, type: MessageType = MessageType.Plain):
    self.message = message
    self.type = type
    self._embed: discord.Embed = None

  @property
  def embed(self):
    return self._embed

  @embed.setter
  def embed(self, embed):
    self._embed = embed
    if self._embed.description == discord.Embed.Empty:
      self._embed.description = self.message

  @staticmethod
  def CreateError(message: str):
    res = Reply(message, MessageType.Error)
    res.embed = discord.Embed(color=0xB30C00, title="Error")
    return res
    
  @staticmethod
  def CreateSuccess(message: str):
    res = Reply(message, MessageType.Success)
    res.embed = discord.Embed(color=0x00B34A, title="Success")
    return res

  @staticmethod
  def CreateConfirmation(message: str):
    res = Reply(message, MessageType.Confirmation)
    res.embed = discord.Embed(color=0xFF9D00, title="Please confirm")
    return res

  @staticmethod
  def CreateEmbed(message: str, title: str):
    res = Reply(message, MessageType.Embed)
    res.embed = discord.Embed(color=0x095DB3, title=title)
    return res

  @staticmethod
  def CreatePlain(message: str):
    res = Reply(message, MessageType.Plain)
    return res



