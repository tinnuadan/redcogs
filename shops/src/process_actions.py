import typing
import copy
from discord import Embed

from .actions import Action, ActionType
from .coordinates import Coordinates, World
from .shopmanager import ShopManager, SearchKey
from .shop import Shop
from .backend import sqlitebackend
from .reply import Reply
from .item import Item


def process_action(manager: ShopManager, action: Action, confirmed: bool = False) -> Reply:
  mgr = manager
  type = action.type
  if type == ActionType.add:
    return _action_add(mgr, action)
  if type == ActionType.update:
    return _action_update(mgr, action)
  if type == ActionType.remove:
    return _action_remove(mgr, action, confirmed)
  if type == ActionType.add_item:
    return _action_add_item(mgr, action)
  if type == ActionType.update_item:
    return _action_update_item(mgr, action)
  if type == ActionType.remove_item:
    return _action_remove_item(mgr, action, confirmed)
  if type == ActionType.show:
    return _action_show(mgr, action)
  if type == ActionType.list:
    return _action_list(mgr, action)
  if type == ActionType.search:
    return _action_search(mgr, action)

  return Reply.CreateError("Action not found")

def _action_search(mgr, action: Action):
  needle = None
  searchKey = SearchKey.Any
  pl = action.payload
  if _get_or_default(pl, 'needle') != None:
    needle = pl['needle']
  elif _get_or_default(pl, 'name') != None:
    needle = pl['name']
    searchKey = SearchKey.Name
  elif _get_or_default(pl, 'owner') != None:
    needle = pl['owner']
    searchKey = SearchKey.Owner
  elif _get_or_default(pl, 'item') != None:
    needle = pl['item']
    searchKey = SearchKey.Items
  result = mgr.searchShop(needle, searchKey)
  if len(result) > 5:
    return Reply.CreateError("The search returned more than 5 results. Please specify your search.")
  if len(result) == 0:
    return Reply.CreatePlain("Nothing matched your search criteria.")
  res = []
  for r in result:
    res.append(_do_action_show(mgr, r.id, False))
  return res


def _action_show(mgr, action: Action):
  id = _pop_id(action.payload)
  verbose = action.payload['verbose']
  return _do_action_show(mgr, id, verbose)

def _do_action_show(mgr, id, verbose):
  def item_to_str(item, verbose):
    res = f"{item.name}"
    if verbose:
      res += f" (ID {item.id})"
    if item.price:
      res += f" sold for {item.price}"
    return res

  shop = mgr.getShop(id)
  if shop == None:
    return Reply.CreateError(f"Shop with the id {id} not found")
  owner = "N.N."
  if len(shop.owner) != 0 and shop.owner != None:
    owner = ", ".join(shop.owner)
  items = "\n".join(list(map(lambda x: item_to_str(x, verbose), shop.items)))
  if len(shop.items) == 0:
    items = "No items sold yet"
  res = Reply.CreateEmbed(None, f"{shop.name} (ID {shop.id})" if verbose else f"{shop.name}")
  embed: Embed = res.embed
  print(embed)
  print(owner)
  embed.add_field(name="Owner", value=owner, inline=True)
  print(embed)
  embed.add_field(name="Location", value=str(shop.coords), inline=True)
  embed.add_field(name="World", value=str(shop.coords.world), inline=True)
  embed.add_field(name="Sold Items", value=items, inline=False)
  if shop.post != None:
    embed.add_field(name="Announcenment Post", value=shop.post, inline=False)
  if shop.coords.isValid:
    embed.add_field(name="Show on Dynmap", value=shop.coords.getDynmapUrl(), inline=False)
  return res


def _action_list(mgr, action: Action):
  list = mgr.list()
  msg = []
  for shop in list:
     msg.append(f"{shop.id:3}: {shop.name}")
  s="\n".join(msg)
  if len(msg) > 0:
    return Reply.CreatePlain(f"```{s}```")#``, f"List of all shops")
  return Reply.CreatePlain("No shops created yet")


def _action_add(mgr, action: Action):
  shop = _create_shop(action.payload)
  shop = mgr.addShop(shop)
  if shop:
    return Reply.CreateSuccess(f"New shop \"{shop.name}\" with id \"{shop.id}\" added.")
  else:
    return Reply.CreateError(f"Unable to add the new shop")

def _action_update(mgr, action: Action):
  id = _pop_id(action.payload)
  shop = mgr.getShop(id)
  if shop == None:
    return Reply.CreateError(f"Shop with the id {id} not found")
  shop_updated = mgr.updateShop(shop, _clone_shop_if_not_set(shop, action.payload))
  if shop_updated:
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

def _action_add_item(mgr, action: Action):
  id = _pop_id(action.payload, 'shop-id')
  shop: Shop = mgr.getShop(id)
  if shop == None:
    return Reply.CreateError(f"Shop with the id {id} not found")
  newvalue = copy.deepcopy(shop)
  itm = _create_item(action.payload)
  newvalue.items.append(itm)
  updated = mgr.updateShop(shop, newvalue)
  if updated and len(updated.items) == len(shop.items)+1:
    return Reply.CreateSuccess(f"The new item \"{itm.name}\" was added to the shop \"{shop.name}\".")
  else:
    return Reply.CreateError(f"Unable to add the new item")

def _action_update_item(mgr, action: Action):
  id = _pop_id(action.payload, 'item-id')
  item_orig = mgr.getItem(id)
  if item_orig == None:
    return Reply.CreateError(f"Item with the id {id} not found")
  item_new = _clone_item_if_not_set(item_orig, action.payload)
  item_orig.name = item_new.name
  item_orig.price = item_new.price
  shop = item_orig.shop
  shop_updated = mgr.updateShop(shop, shop)
  if shop_updated != None:
    return Reply.CreateSuccess(f"The item \"{item_orig.name}\" (belonging to \"{shop.name}\") was updated")
  else:
    return Reply.CreateError(f"Unable to update the item \"{item_orig.name}\"")

def _action_remove_item(mgr, action: Action, confirm):
  id = action.payload['item-id']
  item = mgr.getItem(id)
  if item == None:
    return Reply.CreateError(f"Item with the id {id} not found")
  if confirm:
    shop_new = item.shop
    shop_orig = copy.deepcopy(shop_new)
    shop_new.items.remove(item)
    shop_updated = mgr.updateShop(shop_orig, shop_new)
    if len(shop_updated.items) == len(shop_orig.items) - 1:
      return Reply.CreateSuccess(f"The item \"{item.name}\" (belonging to \"{shop_orig.name}\") was removed")
    else:
      return Reply.CreateError(f"Unable to remove the item \"{item.name}\"")
  else:
    return Reply.CreateConfirmation(f"Are you sure you want to remove the item \"{item.name}\" (belonging to \"{item.shop.name}\")?")

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
  for itm_str in _get_or_default(payload, 'item', []):
    tmp = itm_str.split(":")
    pl = { 'name': tmp[0]}
    if len(tmp)==2:
      pl['price'] = tmp[1]
    res.items.append(_create_item(pl))
  return res

def _create_item(payload: typing.Dict):
  res = Item()
  res.name = _get_or_default(payload, 'name', '')
  res.price = _get_or_default(payload, 'price', '')
  return res

def _clone_shop_if_not_set(shop: Shop, payload: typing.Dict):
  coords = Coordinates()
  coords.x = _get_or_default(payload, 'x', shop.coords.x)
  coords.y = _get_or_default(payload, 'y', shop.coords.y)
  coords.z = _get_or_default(payload, 'z', shop.coords.z)
  coords.world = _get_or_default(payload, 'world', shop.coords.world)

  res = Shop()
  res.name = _get_or_default(payload, 'name', shop.name)
  res.coords = coords
  res.owner = _get_or_default(payload, 'owner', shop.owner)
  items = _get_or_default(payload, 'item', [])
  if len(items) != 0:
    for itm_str in items:
      tmp = itm_str.split(":")
      pl = { 'name': tmp[0]}
      if len(tmp)==2:
        pl['price'] = tmp[1]
      res.items.append(_create_item(pl))
  else:
    res.items = shop.items
  return res

def _clone_item_if_not_set(item: Item, payload: typing.Dict):
  res = Item()
  res.name = _get_or_default(payload, 'name', item.name)
  res.price = _get_or_default(payload, 'price', item.price)
  return res