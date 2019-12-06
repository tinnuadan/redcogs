import enum

class ActionType(enum.Enum):
  ERROR = enum.auto()
  add = enum.auto()
  update = enum.auto()
  remove = enum.auto()
  show = enum.auto()
  search = enum.auto()
  list = enum.auto()
  add_item = enum.auto()
  update_item = enum.auto()
  remove_item = enum.auto()
  help = enum.auto()

class Action:
  _confirmation_needed = [ActionType.remove, ActionType.remove_item]
  def __init__(self, type: ActionType, payload = None):
    self.type = type
    self.payload = payload

  @property
  def confirmationNeeded(self) -> bool:
    return self.type in Action._confirmation_needed

  @property
  def isHelp(self) -> bool:
    return self.type == ActionType.help

  @property
  def isError(self) -> bool:
    return self.type == ActionType.ERROR
