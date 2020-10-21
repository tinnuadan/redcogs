# Shops
Shop cog for keeping a database of Minecraft shops

## Commands
To show all available commands do `!shop --help`. To get help for a specific command do `!shop <command> --help`.

The commands are:

```
add         -  Add a shop.
search      -  Search for shop
show        -  Show verbose shop details
list        -  List all shops.
remove      -  Remove a shop.
update      -  Edit a shop. Only provided values will be changed.
add-item    -  Add an item to a shop.
remove-item -  Remove an item from a shop.
update-item -  Edit an item. Only provided values will be changed.
```

### General remarks
If you type a string which contains spaces you have to use double quotes.

## Add Shop
Add a shop with `!shop add [-o OWNER] [-i ITEM] [-x X] [-y Y] [-z Z] [-w WORLD] [-p POST] name`

The only required argument is the name. If it contains a space encase it in double quotes.
### Owner
You can set an owner with `-o OWNER` or `--owner OWNER`. You can also specify multiple owners by `-o OWNER1 -o OWNER2`. Use double quotes if the name contains a space.
### Items
You can set the sold items with `-i ITEM:PRICE` or `--item ITEM:PRICE`. You can also specify multiple sold items by `-i ITEM1:PRICE1 -i ITEM1:PRICE1`. Use double quotes if the the whole string contains a space. You can also add items later.
### Coordinates
You can set the coordinates of the shop with `-x X -y Y -z Z`. Usually you only have to specify y if it's not on the surface.

If your shop is not located in the overworld you might want to set it with `-w WORLD` (or `--world WORLD`) where WORLD is 1 for the overworld, 2 for the nether and 3 for the end.
### Post
You can link a discord announcement post with `-p POST` or `--p POST`

## Search
Search for a shop with `!shop search [-n NAME] [-o OWNER] [-i ITEM] [-v] [needle]`

You can use `!shop search <needle>` to search for `needle` in all fields (i.e. name of the shop, owners and sold items) or  search specificily for any of those fields. For example you can search for a specific sold item with `!shop search -i ITEM` (or `!shop search --item ITEM`).

All search commands implcitly use wildcards and are case insensitive, so `!shop search axe` would also find "pickaxe".

Use `-v` to increase the verbosity of your results (i.e. it will show the ID of the items and the shop which you need for updating and removing)

## Show
Show just one shop with `!shop show [-v] id` where `id` is either the numeric ID or the exact shop name (case insensitive).

Use `-v` to increase the verbosity of your results (i.e. it will show the ID of the items and the shop which you need for updating and removing)

## List
List the numeric id and the name of all shops with `!shop list`

## Update
Update a shop with `!shop update [-h] [-n NAME] [-o OWNER] [-i ITEM] [-x X] [-y Y] [-z Z] [-w WORLD] [-p POST] id`. Specify the numeric `id` and whatever you want to change. Everything else won't be changed. 

See the usage of `add` for details.

ATTENTION: Be aware that the whole list of items will be overwritten if you use `-i ITEM` (or `--item ITEM`). Consider `add-item`, `update-item` or `remove-item` instead.

## Remove
Remove the shop with the numeric `id` with `!shop remove id`. You have to confirm the removing.

## Add-Item
Add an item with `!shop add-item [-p PRICE] shop-id name`. Specify the numeric `shop-id` the name of the item and an optional price.

## Update-Item
Update an item with `!shop update-item [-n NAME] [-p PRICE] item-id`. Specify the numeric `item-id` and change the name and/or the price. Any value not specified will be not changed.

## Remove-Item
Remove the item with the numeric `item-id` with `!shop update-item item-id`.  You have to confirm the removing.
