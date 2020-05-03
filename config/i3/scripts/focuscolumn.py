#!/usr/bin/python3
#
# This script implements interesting operations for i3 when you work with a two
# columns layout at the workspace level. It enables three basic operations that
# you can bind to different keys:
#
#   1. whit no options the script changes the focus to the other colum,
#      regardless of the layout in the containers of each column
#   2. with -s (swap), the script swaps the focused window with the focus
#      inactive one in the other column, regardless of the layout in both
#      columns
#   3. with -m (move), the script moves the window to the other column,
#      regardless of the layout in both columns
#   4. with -m|-s and -a (alternate), the focus is set at the end on the origin
#      column insted of the destination column
#
# GPL License header
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Author: Christian Tenllado
# Copyright 2020 Christian Tenllado
# e-mail: ctenllado@gmail.com

import optparse
from i3ipc import Connection

options = None
args = None

def parse_options():
    global options
    global args

    usage_str = "%prog [-m -s]"
    parser = optparse.OptionParser(usage_str)
    parser.add_option("-s", action="store_true", dest="swap", default=False,
            help="swap with the focus inactive window in the other column")
    parser.add_option("-m", action="store_true", dest="move", default=False,
            help="move the window to the other column")
    parser.add_option("-a", action="store_true", dest="alternate",
            default=False,
            help="when swaping or moving focus the other column at the end")

    options, args  = parser.parse_args()

def switch_col(con, focused):
    global options, args
    if con.layout == 'splith' and len(con.nodes) == 1 and \
            con.nodes[0].layout == 'splith':
        return switch_col(con.nodes[0], focused)
    elif con.layout != 'splith' or len(con.nodes) != 2:
        return

    if (len(con.nodes[0].nodes) == 0 and con.nodes[0].window == focused.window)\
            or con.nodes[0].find_by_id(focused.id):
        d = 1
    else:
        d = 0

    if len(con.nodes[d].focus) == 0:
        dest = con.nodes[d]
    else:
        dest = con.nodes[d].find_by_id(con.nodes[d].focus[0])

    if options.swap:
        dest.command('mark --add _quickswap')
        focused.command('swap container with mark _quickswap')
        dest.command('unmark _quickswap')
    elif options.move:
        if len(dest.nodes) == 0:
            dest.command('split v')
        dest.command('mark --add _target')
        focused.command('move container to mark _target')
        dest.command('unmark _target')

    if (not options.swap and not options.move) or options.alternate:
        dest.command('focus')

def main():
    parse_options()
    cnx = Connection()
    focused = cnx.get_tree().find_focused()
    wsp = focused.workspace()
    if not wsp or wsp.name == "__i3_scratch":
        return
    switch_col(wsp, focused)

if __name__ == "__main__":
    main()