"""
Utility functions for framework components
"""

# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016  Dominik George <nik@naturalnet.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import inspect
import os
import sys

# Caching variable for the game module
_game_module = None

class NoSuchResourceError(Exception):
    """ Thrown when a resource cannot be found in a game data directory. """

    pass

def get_game_module():
    """ Get the module object of the calling game, or None """

    global _game_module

    if _game_module:
        # Return cached module if already found
        return _game_module
    else:
        # Get full call stack; skip first two frames (inspect and us)
        _stack = inspect.stack()
        for _frame in  _stack[2:]:
            # Get module from frame
            _module = inspect.getmodule(_frame[0])

            # Check if module is outside of us
            if _module and not _module.__name__ == __name__:
                _game_module = _module
                return _game_module

    # If we got here, caller could not be identified
    _game_module = None
    return _game_module

def get_game_module_name():
    """ Get the module name of the calling game, or None """

    return get_game_module().__name__

def get_game_data_file_name(restype, basename):
    """
    Get the full path of a game data resource.

    Keyword arguments:

    restype -- type of the resource to be loaded; one of:
               image - for image files
    basename -- basename of the file to find; without extension
                so a logical decision can be made by type
    """

    # Get the calling module
    _module = get_game_module_name()
    # Get the path of the module implementation
    _modpath = os.path.dirname(sys.modules[_module].__file__)
    # Get path of data directory for given type
    _respath = os.path.join(_modpath, "data", restype)

    # Logic depending on resource type to be loaded
    if restype == "image":
        # Check whether a PNG file exists
        _file = os.path.join(_respath, "%s.png" % basename)
        if os.path.isfile(_file):
            return _file

    # If we got here, no logic matched
    raise NoSuchResourceError("No resource found for game %s, type %s, called %s; looked inside <%s>."
                              % (_module, restype, basename, _respath))
