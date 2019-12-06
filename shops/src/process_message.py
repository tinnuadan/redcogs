import argparse
from typing import List, Dict
import io
import shlex
from . import actions

class CustomHelpFormatter(argparse.HelpFormatter):
  def __init__(self,
                prog,
                indent_increment=2,
                max_help_position=60,
                width=200):
    super().__init__(prog, indent_increment, max_help_position, width)

  def _format_action(self, action):
    if type(action) == argparse._SubParsersAction:
      # inject new class variable for subcommand formatting
      subactions = action._get_subactions()
      invocations = [self._format_action_invocation(a) for a in subactions]
      self._subcommand_max_length = max(len(i) for i in invocations)

    if type(action) == argparse._SubParsersAction._ChoicesPseudoAction:
      # format subcommand help line
      subcommand = self._format_action_invocation(action) # type: str
      width = self._subcommand_max_length
      help_text = ""
      if action.help:
        help_text = self._expand_help(action)
      return "  {:{width}} -  {}\n".format(subcommand, help_text, width=width)

    elif type(action) == argparse._SubParsersAction:
      # process subcommand help section
      msg = '\n'
      for subaction in action._get_subactions():
        msg += self._format_action(subaction)
      return msg
    else:
      return super(CustomHelpFormatter, self)._format_action(action)

### This parser doesn't call sys.exit() but just sets a global flag to stop subparsers from reporting
### It provides a posibility to reroute messages to a file
class CustomArgParser(argparse.ArgumentParser):
   #static because it's shared with the subparsers
  _finished = False
  vfile = None

  def __init__(self,
              prog=None,
              usage=None,
              description=None,
              epilog=None,
              parents=[],
              formatter_class=argparse.HelpFormatter,
              prefix_chars='-',
              fromfile_prefix_chars=None,
              argument_default=None,
              conflict_handler='error',
              add_help=True,
              allow_abbrev=True):
    super().__init__(prog, usage, description, epilog, parents, 
                      formatter_class, prefix_chars, fromfile_prefix_chars,
                      argument_default, conflict_handler, add_help, allow_abbrev)

  def exit(self, status=0, message=None):
    if CustomArgParser._finished:
      return
    CustomArgParser._finished = True

  def get_usage(self):
    return self.format_usage()

  def get_help(self):
    return self.format_help()

  def _print_message(self, message, file = None):
    return super()._print_message(message, CustomArgParser.vfile)

def parse_message(msg):
  parser = CustomArgParser(prog="!shop",formatter_class=CustomHelpFormatter)
  subparsers = parser.add_subparsers(dest='action_name')
  parser_add = subparsers.add_parser("add", help="Add a shop.",formatter_class=CustomHelpFormatter)
  parser_add.add_argument('name', type=str, help='The name of the shop')
  parser_add.add_argument('-o', '--owner', action='append', type=str, help='The owner[s] of the shop. You can specify multiple.')
  parser_add.add_argument('-i', '--item', action='append', type=str, help='The sold item[s] in the shop. You can specify multiple and add a price by doing \'item:price\'')
  parser_add.add_argument('-x', default=None, type=int, help='x-coordinate of the location of the shop')
  parser_add.add_argument('-y', default=None, type=int, help='y-coordinate of the location of the shop')
  parser_add.add_argument('-z', default=None, type=int, help='z-coordinate of the location of the shop')
  parser_add.add_argument('-w', '--world', default=None, type=int, help='world (1: overworld, 2: nether, 3: end)')
  parser_add.add_argument('-p', '--post', default=None, type=str, help='A link to the announcent post')

  parser_find = subparsers.add_parser("search", help="Search for shop", formatter_class=CustomHelpFormatter)
  parser_find.add_argument('needle', nargs='?', default=None, type=str, help='Search in all fields for NEEDLE')
  parser_find.add_argument('-n', '--name', default=None, type=str, help='Search for NAME in the name of the shop')
  parser_find.add_argument('-o', '--owner', default=None, type=str, help='Search for OWNER')
  parser_find.add_argument('-i', '--item', default=None, type=str, help='Search for ITEM')
  parser_find.add_argument('-v', '--verbose', action='store_true', help='Show more details')

  parser_show = subparsers.add_parser("show", help="Show verbose shop details", formatter_class=CustomHelpFormatter)
  parser_show.add_argument('id', help='The id or exact name of the shop')
  parser_show.add_argument('-v', '--verbose', action='store_true', help='Show more details')

  subparsers.add_parser("list", help="List all shops.", formatter_class=CustomHelpFormatter)

  parser_remove = subparsers.add_parser("remove", help="Remove a shop.", formatter_class=CustomHelpFormatter)
  parser_remove.add_argument('id', type=int, help='The id of the shop')

  parser_edit = subparsers.add_parser("update", help="Edit a shop. Only provided values will be changed.")
  parser_edit.add_argument('id', type=int, help='the id of the shop')
  parser_edit.add_argument('-n', '--name', default=None, type=str, help='the name of the shop')
  parser_edit.add_argument('-o', '--owner', action='append', type=str, help='the owner of the shop')
  parser_edit.add_argument('-i', '--item', action='append', type=str, help='the owner of the shop')
  parser_edit.add_argument('-x', default=None, type=int, help='x-coordinate of the location of the shop')
  parser_edit.add_argument('-y', default=None, type=int, help='y-coordinate of the location of the shop')
  parser_edit.add_argument('-z', default=None, type=int, help='z-coordinate of the location of the shop')
  parser_edit.add_argument('-w', '--world', default=None, type=int, help='world (1: overworld, 2: nether, 3: end)')
  parser_edit.add_argument('-p', '--post', default=None, type=str, help='A link to the announcent post')

  parser_add_item = subparsers.add_parser("add-item", help="Add an item to a shop.",formatter_class=CustomHelpFormatter)
  parser_add_item.add_argument('shop-id', type=int, help='the id of the shop')
  parser_add_item.add_argument('name', type=str, help='The name of the item')
  parser_add_item.add_argument('-p', '--price', default=None, type=str, help='An optional price for the item')

  parser_remove_item = subparsers.add_parser("remove-item", help="Remove an item from a shop.",formatter_class=CustomHelpFormatter)
  parser_remove_item.add_argument('item-id', type=str, help='The id of the item')

  parser_update_item = subparsers.add_parser("update-item", help="Edit an item. Only provided values will be changed.",formatter_class=CustomHelpFormatter)
  parser_update_item.add_argument('item-id', type=int, help='The id of the item')
  parser_update_item.add_argument('-n', '--name', type=str, help='The new name of the item')
  parser_update_item.add_argument('-p', '--price', default=None, type=str, help='The new price of the item')


  #setup getting the message
  CustomArgParser.vfile = io.StringIO()
  args = None
  try:
    args = parser.parse_args(shlex.split(msg))
    message = CustomArgParser.vfile.getvalue()
  except TypeError:
    message = "Invalid command\n"
    message += parser.get_usage()
    pass
  CustomArgParser.vfile.close()
  CustomArgParser.vfile = None

  if message != "":
    return actions.Action(actions.ActionType.help, message)
  
  args = vars(args)
  action_name = args['action_name'].replace("-","_")
  return actions.Action(actions.ActionType[action_name], args)





  


