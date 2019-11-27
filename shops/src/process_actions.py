import typing

from .actions import Action, ActionType
from .coordinates import Coordinates, World
from .shopmanager import ShopManager, SearchKey
from .shop import Shop
from .backend import sqlitebackend
from .reply import Reply

def process_action(manager: ShopManager, action: Action, confirmed: bool = False) -> Reply:
  mgr = manager
  type = action.type
  if type == ActionType.add:
    return _action_add(mgr, action)
  if type == ActionType.show:
    return _action_show(mgr, action)
  if type == ActionType.update:
    return _action_update(mgr, action)
  if type == ActionType.remove:
    return _action_remove(mgr, action, confirmed)
  
  return Reply.CreateError("Action not found")

def _action_add(mgr, action: Action):
  shop = mgr.addShop(_create_shop(action.payload))
  if shop:
    return Reply.CreateSuccess(f"New shop \"{shop.name}\" with id \"{shop.id}\" added.")
  else:
    return Reply.CreateError(f"Unable to add the new shop")

def _action_show(mgr, action: Action):
  id = _pop_id(action.payload)
  shop = mgr.getShop(id)
  if shop == None:
    return Reply.CreateError(f"Shop with the id {id} not found")
  owner = ", ".join(shop.owner)
  msg = f"Shop: {shop.name}\nOwner: {owner}"
  return Reply.CreateEmbed(msg, f"Details for {shop.name}")

def _action_update(mgr, action: Action):
  id = _pop_id(action.payload)
  shop = mgr.getShop(id)
  if shop == None:
    return Reply.CreateError(f"Shop with the id {id} not found")
  shop_updated = mgr.updateShop(shop, _copy_if_not_set(shop, action.payload))
  if not shop_updated:
    return Reply.CreateSuccess(f"The shop \"{shop.name}\" was updated")
  else:
    return Reply.CreateError(f"Unable to update the shop \"{shop.name}\"")
  
def _action_remove(mgr, action: Action, confirm):
  id = action.payload['id']
  shop = mgr.getShop(id)
  if shop == None:
    return Reply.CreateError(f"Shop with the id {id} not found")
  if confirm:
    success = mgr.removeShop(shop)
    if success:
      return Reply.CreateSuccess(f"The shop \"{shop.name}\" was removed")
    else:
      return Reply.CreateError(f"Unable to remove the shop \"{shop.name}\"")
  else:
    return Reply.CreateConfirmation(f"Are you sure you want to remove the shop \"{shop.name}\"?")

# helpers
T = typing.TypeVar('T')

def _pop_id(payload: dict, key = 'id') -> typing.Any:
  result = 0
  if key in payload:
    result = payload[key]
    del payload[key]
  return result

def _get_or_default(d: typing.Dict, key: typing.Any, default: T = None) -> T:
  return d[key] if key in d and d[key]!=None else default

def _create_shop(payload: typing.Dict):
  coords = Coordinates()
  coords.x = _get_or_default(payload, 'x', None)
  coords.y = _get_or_default(payload, 'y', None)
  coords.z = _get_or_default(payload, 'z', None)
  coords.world = World.Overworld

  res = Shop()
  res.name = _get_or_default(payload, 'name', '')
  res.coords = coords
  res.owner = _get_or_default(payload, 'owner', [])
  return res

def _copy_if_not_set(shop: Shop, payload: typing.Dict):
  coords = Coordinates()
  coords.x = _get_or_default(payload, 'x', shop.coords.x)
  coords.y = _get_or_default(payload, 'y', shop.coords.y)
  coords.z = _get_or_default(payload, 'z', shop.coords.z)
  coords.world = _get_or_default(payload, 'z', shop.coords.world)

  res = Shop()
  print(shop.name)
  res.name = _get_or_default(payload, 'name', shop.name)
  res.coords = coords
  res.owner = _get_or_default(payload, 'owner', shop.owner)
  return res