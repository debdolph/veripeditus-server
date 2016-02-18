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
import pkgutil
import sys
from wand.image import Image

class NoSuchResourceError(Exception):
    """ Thrown when a resource cannot be found in a game data directory. """

    pass

def get_game_module():
    """ Get the module object of the calling game, or None """

    # Get full call stack; skip first two frames (inspect and us)
    _stack = inspect.stack()
    for _frame in  _stack[1:]:
        # Get module from frame
        _module = inspect.getmodule(_frame[0])

        # Check if module is outside of us
        if _module and not _module.__name__.startswith("veripeditus.framework"):
            return _module

def get_game_module_name():
    """ Get the module name of the calling game, or None """

    return get_game_module().__name__

def get_game_data_file_name(restype, basename):
    """
    Get the full path of a game data resource.

    Keyword arguments:

    restype -- type of the resource to be loaded; one of:
                image - for image files
                text - for text files
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
    elif restype == "text":
        # Check whether a TXT file exists
        _file = os.path.join(_respath, "%s.txt" % basename)
        if os.path.isfile(_file):
            return _file

    # If we got here, no logic matched
    raise NoSuchResourceError("No resource found for game %s, type %s, called %s."
                              % (_module, restype, basename))

def get_game_data_file(restype, basename, mode=None):
    """
    Get a file object of a game data resource, in read-only mode.

    Keyword arguments:

    restype -- type of the resource to be loaded; one of:
               image - for image files
    basename -- basename of the file to find; without extension
                so a logical decision can be made by type
    mode -- optional argument to manuallz set desired file mode
    """

    # Get the file path
    _filename = get_game_data_file_name(restype, basename)

    # Determine file mode
    if not mode:
        _mode = "r"
        if restype in ["image"]:
            # These resource types are binary
            _mode += "b"
    else:
        # Mode was given as argument
        _mode = mode

    return open(_filename, _mode)

def get_game_data_object(restype, basename):
    """
    Get a file object of a game data resource, in read-only mode.

    Keyword arguments:

    restype -- type of the resource to be loaded; one of:
               image - for image files
    basename -- basename of the file to find; without extension
                so a logical decision can be made by type
    """

    # Get the file object
    _file = get_game_data_file(restype, basename)

    # Check resource type and create a matching object
    _obj = None
    if restype == "image":
        _obj = Image(file=_file)
    elif restype == "text":
        _obj = _file.readlines()

    # Close file and return
    _file.close()
    return _obj

def get_game_names():
    """
    Get a list of names of installed games.

    Returns only the base name, i.e. the third part of the package name
    veripeditus.game.foo.
    """

    # Get all accessible packages that start with veripeditus.game.,
    # strip veripeditus.game. and construct list
    _pkgs = [i[1].split(".")[2] for i in pkgutil.walk_packages()
             if i[1].startswith("veripeditus.game.")]

    return _pkgs
